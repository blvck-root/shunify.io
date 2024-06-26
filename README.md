# Shunify Music Recognition App
- Author: [Mthabisi Ndlovu](https://github.com/blvck-root)
- [forked from](https://github.com/itspoma/audio-fingerprint-identifying-python)
- [landing page](https://blvck-root.github.io/shunify/)

## Project Description
- Shunify is a music recognition app for music lovers to discover new songs.

## How to set up 

1. Run `$ make clean reset` to clean & init database struct
2. Run `$ make tests` to make sure that everything is properly configurated
3. Copy some `.mp3` audio files into `mp3/` directory
4. Run `$ make fingerprint-songs` to analyze audio files & fill your db with hashes
5. Start play any of audio file (from any source) from `mp3/` directory, and run (parallely) `$ make recognize-listen seconds=5`

## How to
- To remove a specific song & related hash from db

  ```bash
  $ python sql-execute.py -q "DELETE FROM songs WHERE id = 6;"
  $ python sql-execute.py -q "DELETE FROM fingerprints WHERE song_fk = 6;"
  ```

## Thanks to
- [Song Recognition Using Audio Fingerprinting](https://hajim.rochester.edu/ece/sites/zduan/teaching/ece472/projects/2019/AudioFingerprinting.pdf)
- [How does Shazam work](http://coding-geek.com/how-shazam-works/)
- [Audio fingerprinting and recognition in Python](https://github.com/worldveil/dejavu)
- [Audio Fingerprinting with Python and Numpy](http://willdrevo.com/fingerprinting-and-audio-recognition-with-python/)
- [Shazam It! Music Recognition Algorithms, Fingerprinting, and Processing](https://www.toptal.com/algorithms/shazam-it-music-processing-fingerprinting-and-recognition)
