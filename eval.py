#!/usr/bin/env python
"""
	Originally cmp_parse.py, adapted to needs here
	Read in text files from test_corpus/clean, one by one
	Generate parse with Annotald, keep in test_corpus/genpsd
	Compare each file to its counterpart in test_corpus/handpsd
	Generate evalb report for each file, in evalb_reports
	Read in results for each file, combine into one report with only results, by genre and overall

	This program uses a parsed Icelandic corpus (https://github.com/mideind/GreynirCorpus)
	to evaluate the performance of different parsers.

	The program compares a test set of hand-parsed texts in Penn Treebank format to an automatically
	parsed output for the same texts. Evalb is used to evaluate the performance.

	A normal way to onfigure this program is to clone the GreynirCorpus repository (from the
	above path) into a separate directory, and then place a symlink to it in the main directory.
	For example:

	$ cd github
	$ git clone https://github.com/mideind/GreynirCorpus
	$ cd ParsingTestPipe
	$ ln -s ../GreynirCorpus/ .
	$ python eval.py



"""

import pathlib
from timeit import default_timer as timer
import subprocess

from reynir import Settings
from reynir.simpletree import SimpleTree
from reynir import Greynir
import helpers

# from reynir import _BIN_Session  # Skoða vel, þetta er í bindb.py

#Settings.read(os.path.join(basepath, "config", "Greynir.conf"))
Settings.DEBUG = False

DATA = 'testset'	# Default value, changed to devset if chosen in argparse
# TODO útfæra að breyta því

CORPUS = pathlib.Path().absolute() / 'GreynirCorpus' / DATA

HANDPSD = pathlib.Path().absolute() / 'data' / DATA / 'handpsd'
GENPSD = pathlib.Path().absolute() / 'data' / DATA / 'genpsd'
BRACKETS = pathlib.Path().absolute() / 'data' / DATA / 'brackets'
TESTFILES = pathlib.Path().absolute() / 'data' / DATA / 'testfiles'
REPORTS = pathlib.Path().absolute() / 'data' / DATA / 'reports'

def process():

	# TODO tékka á argparse hvort vil devset eða testset
	print("Retrieving automatic parse trees")
	helpers.get_annoparse(CORPUS, GENPSD, ".txt", ".psd", False)
	# helpers.get_ipparse(CORPUS, GENPSD, '.txt', '.ippsd', True)

	print("Transforming automatic parse trees to general bracketed form")
	helpers.annotald_to_general(GENPSD, TESTFILES, '.psd', '.grdbr', True, True)
	# helpers.ip_to_general(GENPSD, TESTFILES, ".ippsd", ".ippbr", True)

	print("Retrieving results from evalb")
	# (testfile suffix, goldfile suffix, output file suffix)
	tests = [
		#(".ippbr", ".pbr", ".ippout"), 
		(".grdbr", ".dbr", ".grdout")
	]
	helpers.get_results(BRACKETS, TESTFILES, REPORTS, tests)


	print("Combining reports by genre")
	suffixes = [".grdout",]  # ".grpout", ".ippout"
	genres = ["reynir_corpus" ] #  TODO taka þetta út?

	helpers.combine_reports(REPORTS, suffixes, genres)

def main() -> None:
	#args = parser.parse_args() # TODO
	start = timer()

	process()

	end = timer()
	duration = end - start

	print("")
	print("Running the program took {:f} seconds, or {:f} minutes.".format(duration, (duration / 60.0)))

if __name__ == "__main__":
	main()

