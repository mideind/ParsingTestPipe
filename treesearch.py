#!/usr/bin/env python
"""
	This program searches for given sentence structures in a parsed Icelandic corpus
	(https://github.com/mideind/GreynirCorpus).

	It prints the found structures in an output file.
	
	A description of search pattern syntax can be found at 
	https://greynir.is/doc/patterns.html

	To run the program:
	$ python treesearch.py

"""
import pathlib
import argparse
from timeit import default_timer as timer

#import annotald.treedrawing as TD

from annotald.annotree import AnnoTree as AT
from reynir.simpletree import SimpleTree, AnnoTree
#from reynir.simpletree import AnnoTreeToSimpleTree



parser = argparse.ArgumentParser(
    description=(
        "This program retrieves matches to search patterns"
    )
)

parser.add_argument(
    "-p",
    "--pattern",
    type=str,
    default="",
    help="Retrieve matches for syntax search pattern"
)

def collect_and_search(infolder, pattern):
	""" Collect trees and retrieve search matches """
	# Read trees and store for searching
	i = 0
	for p in infolder.iterdir():
		#if i%10 == 0:
			#print(">>>>>>>>>>>>>>>>>>>>{} files finished!".format(i))
		pin = infolder / p
		#print(p.stem)
		treetext = pin.read_text()
		for each in treetext.split("\n\n"):
			#print(each)
			at = AnnoTree(each)
			print(at._id_local)
			simple = at.as_simple_tree()
			#print(simple.view)
		i+=1


def main() -> None:
	""" Main program """
	# Parse the command line arguments
	args = parser.parse_args() 
	patt = args.pattern
	# TODO skilgreina part - dev eða test
	psdpath = pathlib.Path().absolute() / 'GreynirCorpus' / 'testset' / 'psd'
	collect_and_search(psdpath, patt)


if __name__ == "__main__":
	main()
