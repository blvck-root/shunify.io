#!/usr/bin/python3
import argparse
import os
import struct
import sys

from argparse import RawTextHelpFormatter
from itertools import zip_longest
from termcolor import colored

import libs.fingerprint
import libs.fingerprint.fingerprint

from libs.reader_file import FileReader
from libs.config import get_config
from libs.db_sqlite import SqliteDatabase

if __name__ == '__main__':
  config = get_config()
  db = SqliteDatabase()
  path = "test_audio/"

  parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
  parser.add_argument('-f', '--file', required=True, help='Path to the audio file to recognize')
  args = parser.parse_args()
  file = path + args.file

  # Validate file existence
  if not os.path.isfile(file):
      print(colored(f"Error: File '{file}' does not exist!", 'red'))
      sys.exit(1)

  def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in zip_longest(fillvalue=fillvalue, *args))

  # Load audio data from file
  reader = FileReader(file)
  audio = reader.parse_audio()
  data = audio['channels']

  msg = ' * recorded {} samples'.format(len(data[0]))
  print(colored(msg, attrs=['dark'])) 
  
  channel_amount = len(data)

  result = set()
  matches = []

  def find_matches(samples, Fs=fingerprint.DEFAULT_FS):
      hashes = fp(samples, Fs=Fs)
      return return_matches(hashes)

  def return_matches(hashes):
      mapper = {}
      for hash, offset in hashes:
          mapper[hash.upper()] = offset
      values = list(grouper(mapper.keys(), 1000))

      for split_values in values:
          # TODO: move to db related files
          split_values = list(split_values)
          query = """
              SELECT upper(hash), song_fk, offset
              FROM fingerprints
              WHERE upper(hash) IN (%s)
          """
          query = query % ', '.join('?' * len(split_values))

          x = db.executeAll(query, split_values)

          matches_found = len(x)

          if matches_found > 0:
              msg = '  ** found {} hash matches (step {}/{})'.format(matches_found, len(split_values), len(values))
              print(colored(msg, 'green'))

          else:
              msg = '  ** not matches found (step %d/%d)'.format(len(split_values), len(values))
              print(colored(msg, 'red'))

          for hash, sid, offset in x:
              # (sid, db_offset - song_sampled_offset)
              offset_int = struct.unpack('q', offset)[0]  # assume offset is 8 bytes long
              result = offset_int - mapper[hash]
              yield (sid, result)

  for channeln, channel in enumerate(data):
      # TODO: Remove prints or change them into optional logging.
      msg = '  fingerprinting channel {}/{}'.format(channeln + 1, channel_amount)
      print(colored(msg, attrs=['dark']))

      matches.extend(find_matches(channel))

      msg = '  finished channel {}/{}, got {} hashes'.format(channeln + 1, channel_amount, len(matches))
      print(colored(msg, attrs=['dark']))

  def align_matches(matches):
      diff_counter = {}
      largest = 0
      largest_count = 0
      song_id = -1

      for tup in matches:
          sid, diff = tup

          if diff not in diff_counter:
              diff_counter[diff] = {}

          if sid not in diff_counter[diff]:
              diff_counter[diff][sid] = 0

          diff_counter[diff][sid] += 1

          if diff_counter[diff][sid] > largest_count:
              largest = diff
              largest_count = diff_counter[diff][sid]
              song_id = sid

      song = db.get_song_by_id(song_id)

      nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                       fingerprint.DEFAULT_WINDOW_SIZE *
                       fingerprint.DEFAULT_OVERLAP_RATIO, 5)
      return {
          "SONG_ID": song_id,
	  "SONG_NAME": song[1],
          "CONFIDENCE": largest_count,
          "OFFSET": int(largest),
          "OFFSET_SECS": nseconds
      }

  total_matches_found = len(matches)

  print('')

  if total_matches_found > 0:
    msg = ' ** totally found {} hash matches'.format(total_matches_found)
    print(colored(msg, 'green'))

    song = align_matches(matches)

    msg = ' => song: {} (id={})\n'.format(song['SONG_NAME'], song['SONG_ID'])
    msg += '    offset: {} ({} secs)\n'.format(song['OFFSET'], song['OFFSET_SECS'])
    msg += '    confidence: {}'.format(song['CONFIDENCE'])
    print(colored(msg, 'green'))

  else:
    msg = ' ** not matches found at all'
    print(colored(msg, 'red'))
