#!/usr/bin/env python
"""
	This program searches for given sentence structures in a parsed Icelandic corpus
	(https://github.com/mideind/GreynirCorpus).

	It prints the found structures in an output file.
	
	A description of search pattern syntax can be found at 
	https://greynir.is/doc/patterns.html

	A normal way to configure this program is to clone the GreynirCorpus repository into a 
	separate directory, and then place a symlink to it in the main directory.

	For example:

	$ cd github
	$ git clone https://github.com/mideind/GreynirCorpus
	$ cd ParsingTestPipe
	$ ln -s ../GreynirCorpus/ .

	To run the program:
	$ python treesearch.py -of [outputformat] -p "pattern1" "pattern2"

"""
import pathlib
import argparse
from timeit import default_timer as timer
from collections import defaultdict
#import annotald.treedrawing as TD

from annotald.annotree import AnnoTree as AT
from reynir.simpletree import SimpleTree, AnnoTree
#from reynir.simpletree import AnnoTreeToSimpleTree

ALLTREES = defaultdict(set)

DEVGOLD = pathlib.Path().absolute() / 'GreynirCorpus' / 'devset' / 'psd'
TESTGOLD = pathlib.Path().absolute() / 'GreynirCorpus' / 'testset' / 'psd'
DEVAUTO = pathlib.Path().absolute() / 'data' / 'devset' / 'genpsd' 
TESTAUTO = pathlib.Path().absolute() / 'data' / 'testset' / 'genpsd' 


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


def collect(infolder, searchpart):
	""" Collect trees and store for searching """
	i = 0
	for p in infolder.iterdir():
		#print(p)
		if i%10 == 0:
			print(">>>>>>>>>>>>>>>>>>>>{} files finished!".format(i))
		pin = infolder / p
		#print(p.stem)
		treetext = pin.read_text()
		for each in treetext.split("\n\n"):
			if not each:
				# Empty line before EOF
				continue
			#print(each)
			at = AnnoTree(each)
			opening = each.count("(")
			closing = each.count(")")
			if opening != closing:
				print("PASSAR EKKI: {}\t{}".format(at._id_local, opening-closing))
			#print(at._id_local)
			simple = at.as_simple_tree()
			#print(simple.view)
			if not simple:
				# Couldn't read as a tree.
				print("FEKK EKKI: {}".format(at._id_local))
			ALLTREES[searchpart].add((simple, at._id_local))
		i+=1

def search(patterns, resultpath, outputformat, searchpart):
	""" Retrieve search matches from tree collection """
	i = 1
	print(len(ALLTREES[searchpart]))
	for patt in patterns:
		textblob = []
		textblob.append(patt+"\n")
		for tree, treeid in ALLTREES[searchpart]:
			ms = [x for x in tree.all_matches(patt)]
			if not ms:
				continue
			# Found match(es), storing information
			textblob.append(treeid+"\n")
			if outputformat == 1:
				continue
			elif outputformat == 2:
				for m in ms:
					textblob.append(m.view+"\n\n")
			elif outputformat == 3:
				textblob.append(tree.view+"\n\n")
		filename = "{}{}.out".format(searchpart, i)
		filepath = resultpath / filename
		filepath.write_text("".join(textblob))
		i +=1

def main() -> None:
	""" Main program """
	# Parse the command line arguments
	args = parser.parse_args() 
	patts = args.patterns
	outputformat = args.outputformat
	resultpath = pathlib.Path().absolute() / 'searchresults'

	searchparts = [
		(DEVGOLD, "devgold"),
		(TESTGOLD, "testgold"),
		(DEVAUTO, "devgen"),
		(TESTAUTO, "testgen")
	]

	for psdpath, searchpart in searchparts:
		print("Commencing tree collection - {}".format(searchpart))
		collect(psdpath, searchpart)
		print("Tree collection complete!")
		print("Commencing tree search by patterns - {}".format(searchpart))
		search(patts, resultpath, outputformat, searchpart)

if __name__ == "__main__":
	main()
