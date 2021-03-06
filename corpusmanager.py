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
	$ python corpusmanager.py



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

DATA = 'devset'	# Default value, changed to devset if chosen in argparse
# TODO útfæra að breyta því

# Outside corpora data
CORPUS = pathlib.Path().absolute() / 'GreynirCorpus' / DATA

# Corpora data within the pipeline
GENPSD = pathlib.Path().absolute() / 'data' / DATA / 'genpsd'
BRACKETS = pathlib.Path().absolute() / 'data' / DATA / 'brackets'


class Maker():

	def start(self, overwrite=False):
		print("Transforming handannotated parse trees to general bracketed form")
		# TODO tékka hér á argparse hvort devset eða testset
		helpers.annotald_to_general(CORPUS, BRACKETS, '.gld', '.dbr', True, True)
		# helpers.annotald_to_general(CORPUS, BRACKETS, '.pgld', '.pbr', True, True)


if __name__ == "__main__":

	#ans = input("Do you want to overwrite existing files? (y/n)\n")	# tODO breyta í argparse
	#if ans == "y":
	#	ans = True
	#else:
	#	ans = False
	ans = True	
	start = timer()
	maker = Maker()
	maker.start(ans)
	end = timer()
	duration = end - start
	print("")
	print("Running the program took {:f} seconds, or {:f} minutes.".format(duration, (duration / 60.0)))
