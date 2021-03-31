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

ALLTREES = set()


parser = argparse.ArgumentParser(
    description=(
        "This program retrieves matches to search patterns"
    )
)

parser.add_argument(
    "-p",
    "--patterns",
    nargs="*",
    type=str,
    default=[""],
    help="Retrieve matches for syntax search pattern. Form is: \"pattern1\" \"pattern2\" ..."
)


# Úttaksform
# Bara idnúmer
# Bæði idnúmer og hluttré
# idnúmer og allt tréð

parser.add_argument(
	"-of",
	"--outputformat",
	type=int,
	default=1,
	help="Output format.\n1: Only id number is shown.\n2: id number and partial tree matching pattern is shown.\n3: id number and full tree is shown."
)


def collect(infolder):
	""" Collect trees and store for searching """
	i = 0
	for p in infolder.iterdir():
		if i%10 == 0:
			print(">>>>>>>>>>>>>>>>>>>>{} files finished!".format(i))
		pin = infolder / p
		#print(p.stem)
		treetext = pin.read_text()
		for each in treetext.split("\n\n"):
			#print(each)
			at = AnnoTree(each)
			#print(at._id_local)
			simple = at.as_simple_tree()
			#print(simple.view)
			if not simple:
				continue
			ALLTREES.add((simple, at._id_local))
		i+=1

def search(patterns, resultpath, outputformat):
	""" Retrieve search matches from tree collection """
	i = 0
	for patt in patterns:
		textblob = []
		for tree, treeid in ALLTREES:
			ms = [x for x in tree.all_matches(patt)]
			if not ms:
				continue
			# Found match(es), storing information
			textblob.append(treeid+"\n")
			if outputformat == 1:
				continue
			elif outputformat == 3:
				textblob.append(tree+"\n\n")
			elif outputformat == 2:
				for m in ms:
					textblob.append(m.view+"\n\n")
		filename = "pattern{}.out".format(i)
		filepath = resultpath / filename
		filepath.write_text("".join(textblob))
		i +=1
def main() -> None:
	""" Main program """
	# Parse the command line arguments
	psdpath = pathlib.Path().absolute() / 'GreynirCorpus' / 'devset' / 'psd'
	resultpath = pathlib.Path().absolute() / 'searchresults'
	print("Commencing tree collection")
	collect(psdpath)
	print("Tree collection complete!")
	args = parser.parse_args() 
	patts = args.patterns
	outputformat = args.outputformat
	# TODO skilgreina part - dev eða test
	print("Commencing tree search by patterns")
	search(patts, resultpath, outputformat)

if __name__ == "__main__":
	main()
