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

	A normal way to configure this program is to clone the GreynirCorpus repository (from the
	above path) into a separate directory, and then place a symlink to it in the main directory.
	For example:

	$ cd github
	$ git clone https://github.com/mideind/GreynirCorpus
	$ cd ParsingTestPipe
	$ ln -s ../GreynirCorpus/ .
	$ python eval.py

	To measure the parsers' performance on the test set:
	$ python eval.py -m

	To measure the parsers' performance on the test set
	excluding malformed sentences:
	$ python eval.py -m -x

	To parse the entire development corpus:
	$ python eval.py

	To parse 10 files in the development corpus:
	$ python eval.py -n 10

	To skip results for each category and only give overall results:
	$ python eval.py -m -c

"""

import pathlib
from timeit import default_timer as timer
import subprocess
import argparse

from reynir import Settings
from reynir.simpletree import SimpleTree
from reynir import Greynir
import helpers

# from reynir import _BIN_Session  # Skoða vel, þetta er í bindb.py

#Settings.read(os.path.join(basepath, "config", "Greynir.conf"))
Settings.DEBUG = False

# Define the command line arguments

parser = argparse.ArgumentParser(
    description=(
        "This program evaluates the parsing performance "
        "of various parsers"
    )
)

parser.add_argument(
    "-m",
    "--measure",
    action="store_true",
    help="run measurements on test corpus and output results only",
)
parser.add_argument(
    "-x",
    "--exclude",
    action="store_true",
    help="Exclude malformed sentences",
)

parser.add_argument(
    "-c",
    "--nocat",
    action="store_true",
    help="Skip category results",
)

parser.add_argument(
	"-ow",
	"--overwrite",
	action="store_true",
	help="Overwrite existing files",
)

def process():

	print("Retrieving automatic parse trees")
	helpers.get_annoparse(TEXTS, GENPSD, ".txt", ".psd", OVERWRITE)
	# helpers.get_icenlpparse(TEXTS, GENPSD, '.txt', '.inpsd', OVERWRITE)
	# helpers.get_ipparse(TEXTS, GENPSD, '.txt', '.ippsd', OVERWRITE)

	print("Transforming automatic parse trees to general bracketed form")
	helpers.annotald_to_general(GENPSD, TESTFILES, '.psd', '.grdbr', True, OVERWRITE, EXCLUDE)
	# helpers.icenlp_to_general(GENPSD, TESTFILES, ".inpsd", ".inpbr", OVERWRITE, EXCLUDE)
	# helpers.annotald_to_general(GENPSD, TESTFILES, ".ippsd", ".ipdbr", True, OVERWRITE, EXCLUDE) # FOR ICEPAHC, should work

	print("Transforming handannotated parse trees to general bracketed form")
	helpers.annotald_to_general(GOLDPSD, BRACKETS, '.gld', '.dbr', True, OVERWRITE, EXCLUDE)
	#helpers.annotald_to_general(GOLDPSD, BRACKETS, '.pgld', '.inpbr', OVERWRITE, True)
	#helpers.annotald_to_general(GOLDPSD, BRACKETS, '.gld', '.ipdbr', OVERWRITE, True)

	print("Retrieving results from evalb")
	# (testfile suffix, goldfile suffix, output file suffix)
	tests = [
		#(".inpbr", ".inpbr", ".inpout"), 
		#(".ipdbr", ".ipdbr", ".ipdout"), 
		(".grdbr", ".dbr", ".grdout")
	]
	helpers.get_results(BRACKETS, TESTFILES, REPORTS, tests, EXCLUDE)


	print("Combining reports by genre")
	suffixes = [".grdout",]  # ".grpout", ".inpout", "ipdout"
	genres = ["greynir_corpus" ] #  TODO taka þetta út?

	helpers.combine_reports(REPORTS, suffixes, genres, NOCAT)

def main() -> None:
	args = parser.parse_args() 
	global DATA
	if args.measure:
		DATA = 'testset'
	else:
		DATA = 'devset'
	global TEXTS, GOLDPSD, HANDPSD, GENPSD, BRACKETS, TESTFILES, REPORTS

	TEXTS = pathlib.Path().absolute() / 'GreynirCorpus' / DATA / 'txt'
	GOLDPSD = pathlib.Path().absolute() / 'GreynirCorpus' / DATA / 'psd'
	GENPSD = pathlib.Path().absolute() / 'data' / DATA / 'genpsd'
	BRACKETS = pathlib.Path().absolute() / 'data' / DATA / 'brackets'
	TESTFILES = pathlib.Path().absolute() / 'data' / DATA / 'testfiles'
	REPORTS = pathlib.Path().absolute() / 'data' / DATA / 'reports'

	global EXCLUDE, NOCAT, OVERWRITE

	EXCLUDE = args.exclude
	NOCAT = args.nocat
	OVERWRITE = args.overwrite


	start = timer()

	process()

	end = timer()
	duration = end - start

	print("")
	print("Running the program took {:f} seconds, or {:f} minutes.".format(duration, (duration / 60.0)))

if __name__ == "__main__":
	main()

