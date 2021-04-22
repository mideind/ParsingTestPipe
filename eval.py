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
	
	The same can be done for the icenlp repository (https://github.com/hrafnl/icenlp).

	$ cd github
	$ git clone https://github.com/hrafnl/icenlp
	$ cd ParsingTestPipe
	$ ln -s ../icenlp .

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
    help="run measurements on and output only results for test corpus in GreynirCorpus",
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

parser.add_argument(
    "-p",
    "--parser",
    type=int,
    default=0,
    help=(
        "Parser chosen for evaluation.\n"
        "\t0: GreynirPackage.\n"
        "\t1: IceParser.\n"
        "\t2: IcePaHC."
    ),
)

parser.add_argument(
	"-r",
	"--roles",
	default=False,
	action="store_true",
	help="Run measurements for roles in IceParser instead of phrase structure"
)

def icepahcprocess():
	print("Retrieving automatic parse trees")
	# helpers.get_ipparse(TEXTS, DEEPGEN, '.txt', '.ippsd', OVERWRITE)

	print("Transforming automatic parse trees to general bracketed form")
	# helpers.annotald_to_general(DEEPGEN, DEEPGENBRACKETS, ".ippsd", ".ipdbr", True, OVERWRITE, EXCLUDE) # FOR ICEPAHC, should work

	print("Transforming handannotated parse trees to general bracketed form")
	#helpers.annotald_to_general(DEEPGOLD, DEEPBRACKETS, '.gld', '.ipdbr', OVERWRITE, True)

	print("Retrieving results from evalb")
	# (testfile suffix, goldfile suffix, output file suffix)
	tests = [
		#(".inpbr", ".inpbr", ".inpout"), # TODO this should be uncommented
		#(".ipdbr", ".ipdbr", ".ipdout"), 
		(".grdbr", ".dbr", ".grdout")
	]
	helpers.get_results(DEEPBRACKETS, DEEPGENBRACKETS, DEEPREPORTS, tests, EXCLUDE)


	print("Combining reports by genre")
	suffixes = [".grdout",]  # ".grpout", ".inpout", ".ipdout"  # TODO this should be ".ipdout"
	genres = ["greynir_corpus" ] #  TODO taka þetta út?

	helpers.combine_reports(DEEPREPORTS, suffixes, genres, NOCAT)

def shallowprocess():
	
	print("Transforming automatic parse trees to general bracketed form")
	helpers.icenlp_to_general(SHALLOWGEN, SHALLOWGENBRACKETS, ".psd", ".br", OVERWRITE, EXCLUDE, ROLES)

	print("Transforming handannotated parse trees to general bracketed form")
	helpers.icenlp_to_general(SHALLOWGOLD, SHALLOWGOLDBRACKETS, '.gld', '.br', OVERWRITE, EXCLUDE, ROLES)

	print("Retrieving results from evalb")
	# (testfile suffix, goldfile suffix, output file suffix)
	tests = [(".br", ".br", ".out")]
	helpers.get_results(SHALLOWGOLDBRACKETS, SHALLOWGENBRACKETS, SHALLOWREPORTS, tests, EXCLUDE)

def deepprocess():

	print("Retrieving automatic parse trees")
	helpers.get_annoparse(TEXTS, DEEPGEN, ".txt", ".psd", OVERWRITE)	# TODO this should be commented

	print("Transforming automatic parse trees to general bracketed form")
	helpers.annotald_to_general(DEEPGEN, DEEPGENBRACKETS, '.psd', '.br',OVERWRITE, EXCLUDE)

	print("Transforming handannotated parse trees to general bracketed form")
	helpers.annotald_to_general(DEEPGOLD, DEEPGOLDBRACKETS, '.gld', '.br', OVERWRITE, EXCLUDE)

	print("Retrieving results from evalb")
	# (testfile suffix, goldfile suffix, output file suffix)
	tests = [(".br", ".br", ".out")]
	helpers.get_results(DEEPGOLDBRACKETS, DEEPGENBRACKETS, DEEPREPORTS, tests, EXCLUDE)

	print("Combining reports")

	helpers.combine_reports(DEEPREPORTS)

def main() -> None:
	args = parser.parse_args() 

	global EXCLUDE, NOCAT, OVERWRITE

	EXCLUDE = args.exclude
	NOCAT = args.nocat
	OVERWRITE = args.overwrite

	start = timer()

	if args.parser == 0:
		# GreynirPackage, GreynirCorpus
		global DATA
		if args.measure:
			DATA = 'testset'
		else:
			DATA = 'devset'
		global TEXTS, DEEPGOLD, DEEPGEN, DEEPGOLDBRACKETS, DEEPGENBRACKETS, DEEPREPORTS

		TEXTS = pathlib.Path().absolute() / 'GreynirCorpus' / DATA / 'txt'
		DEEPGOLD = pathlib.Path().absolute() / 'GreynirCorpus' / DATA / 'psd'
		DEEPGEN = pathlib.Path().absolute() / 'data' / DATA / 'genpsd'
		DEEPGOLDBRACKETS = pathlib.Path().absolute() / 'data' / DATA / 'goldbrackets'
		DEEPGENBRACKETS = pathlib.Path().absolute() / 'data' / DATA / 'genbrackets'
		DEEPREPORTS = pathlib.Path().absolute() / 'data' / DATA / 'reports'
		deepprocess()

	elif args.parser == 1:
		# IceParser, icenlp
		global SHALLOWGOLD, SHALLOWGEN, SHALLOWGOLDBRACKETS, SHALLOWGENBRACKETS, SHALLOWREPORTS
		SHALLOWGOLD = pathlib.Path().absolute() / 'icenlp' / 'core' / 'bat' / 'iceparser' / 'testData' / 'test.gold.sent.gold'
		SHALLOWGEN = pathlib.Path().absolute() / 'icenlp' / 'core' / 'bat' / 'iceparser' / 'testData' / 'test.gold.sent.parsed'
		SHALLOWGOLDBRACKETS = pathlib.Path().absolute() / 'data' / 'shallow' / 'goldbrackets'
		SHALLOWGENBRACKETS = pathlib.Path().absolute() / 'data' / 'shallow' / 'genbrackets'
		SHALLOWREPORTS = pathlib.Path().absolute() / 'data' / 'shallow' / 'reports'

		global ROLES
		ROLES = args.roles
		shallowprocess()

	elif args.parser == 2:
		# Berkeley parser, IcePaHC
		icepahcprocess()
	else:
		pass

	end = timer()
	duration = end - start

	print("")
	print("Running the program took {:f} seconds, or {:f} minutes.".format(duration, (duration / 60.0)))

if __name__ == "__main__":
	main()

