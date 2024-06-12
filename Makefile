.PHONY: tests

install:
	@echo soon

clean:
	@find . -name \*.pyc -delete

reset:
	@python resetdb.py

tests:
	@python tests/*.py

stats:
	@python getstats.py

fingerprint-songs: clean
	@python collect_fingerprints.py

recognize-listen: clean
	@python identify_mic.py -s $(seconds)

recognize-file: clean
	@python identify_file.py -f $(file)
