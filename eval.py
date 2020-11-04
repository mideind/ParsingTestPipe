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

_DEV_PATH = pathlib.Path().absolute() / 'GreynirCorpus' / 'devset'
_TEST_PATH = pathlib.Path().absolute() / 'GreynirCorpus' / 'testset'


HANDPSD = pathlib.Path().absolute() / 'test_corpus' / 'handpsd'
GENPSD = pathlib.Path().absolute() / 'test_corpus' / 'genpsd'
CLEAN = pathlib.Path().absolute() / 'test_corpus' / 'clean'
BRACKETS = pathlib.Path().absolute() / 'test_corpus' / 'brackets'
TESTFILES = pathlib.Path().absolute() / 'test_corpus' / 'testfiles'
REPORTS = pathlib.Path().absolute() / 'test_corpus' / 'reports'


class Comparison():
	def __init__(self):
		self.results = {}

	def start(self, overwrite=False):

		# Hef textaskjöl
		# Útbý véldjúpþáttuð Greynisskjöl á Annotaldsformi
		helpers.get_annoparse(CLEAN, GENPSD, ".txt", ".psd", True)
		
		# helpers.get_ipparse(CLEAN, GENPSD, '.txt', '.ippsd', True)

		print("Transforming greynir testfiles")
		helpers.annotald_to_general(GENPSD, TESTFILES, '.psd', '.grdbr', True, True)
		
		# print("Transforming IceParser testfiles")
		# helpers.ip_to_general(GENPSD, TESTFILES, ".ippsd", ".ippbr", True)

		# ("testfile suffix", "goldfile suffix", "output file suffix")
		tests = [
			#(".ippbr", ".pbr", ".ippout"), 
			(".grdbr", ".dbr", ".grdout")
		]
		helpers.get_results(BRACKETS, TESTFILES, REPORTS, tests)

		suffixes = [".grdout",]  # ".grpout", ".ippout"
		genres = ["reynir_corpus", "althingi", "visindavefur", "textasafn"]

		helpers.combine_reports(REPORTS, suffixes, genres)


if __name__ == "__main__":

	ans = input("Do you want to overwrite existing files? (y/n)\n")	
	# TODO eftir að breyta ans í True/False gildi
	if ans == "y":
		ans = True
	else:
		ans = False
	start = timer()

	comp = Comparison()
	comp.start(ans)
	end = timer()
	duration = end - start
	print("")
	print("Running the program took {:f} seconds, or {:f} minutes.".format(duration, (duration / 60.0)))
