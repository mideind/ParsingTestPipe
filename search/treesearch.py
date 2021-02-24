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
from annotald.annotree import AnnoTree
from reynir.simpletree import SimpleTree
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
	for p in infolder.iterdir():
		pin = infolder / p
		treetext = AnnoTree.read_from_file(pin)
		for each in treetext:
			if each.label() == "META":
				continue
			simple = SimpleTree.from_annotree(each)
			#print(each.leaves()[1])
			#for child in each:
				#print(child.label())

		#treetext = pin.read_text()
		#treetext = util.scrubText(treetext)
		#trees = treetext.strip().split("\n\n")




	"""

	cat = d["t"].split("_") -- bara orðflokkurinn
		varpa honum svo í erlendu heitin - N, PRO, ...


annoaðferðir:
	label - skilar node label of tree
	leaves - skilar öllum laufum trésins í lista; gæti fengið toklist svona!
		toklist er tree.leaves()[3:] -- sleppi þá lýsigögnum
		skjal og setning er tree.leaves()[1]
	for child in node:
		if isinstance(child, Tree):
			skoða áfram
	is_terminal


	root - tréið
	
	# token list lítur svona út
	# [[WORD: Hestur], [WORD: datt], [PUNCTUATION: .]]


	Byrjar á að lesa öll tré í set sem SimpleTree
	Les líka inn í dict, SimpleTree : [skjal+setnnr]  - getur verið mörg
	Ef finnur match, skrifar í skjal
	skjal+setnnr, undirtréð sem kemur við sögu

	{'x': 'Hér', 'ix': 0, 't': 'ao', 'k': 'WORD', 's': 'hér', 'c': 'ao', 'f': 'alm', 'b': '-', 'a': 'ao'}
	{'x': 'er', 'ix': 1, 't': 'so_0_et_p3', 'k': 'WORD', 's': 'vera', 'c': 'so', 'f': 'alm', 'b': 'GM-FH-NT-3P-ET', 'a': 'so_0_et_fh_gm_nt_p3'}
	{'x': 'hestur', 'ix': 2, 't': 'no_et_nf_kk', 'k': 'WORD', 's': 'hestur', 'c': 'kk', 'f': 'alm', 'b': 'NFET', 'a': 'no_et_kk_nf'}
	{'x': '.', 'ix': 3, 'k': 'PUNCTUATION'}


	mætti bæta við leitina ^liður? Þá útiloka að birtist einhver staðar?
	"""



def main() -> None:
	""" Main program """
	# Parse the command line arguments
	args = parser.parse_args() 
	patt = args.pattern
	# TODO skilgreina part - dev eða test
	psdpath = pathlib.Path().absolute() / 'brackets'	# TODO pathlib.Path().absolute() / 'GreynirCorpus' / DATA / 'psd'
	# TODO nei, breyta í DEV eða TEST og brackets


	collect_and_search(psdpath, patt)


if __name__ == "__main__":
	main()
