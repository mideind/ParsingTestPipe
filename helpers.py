#!/usr/bin/env python

import os
import pathlib
import subprocess
from collections import defaultdict
import itertools

from reynir.simpletree import SimpleTree
import annotald.util as util

EVALBCOMMAND = ' -p ./stillingar.prm' # handpsd is first argument, then genpsd
ICENLP = pathlib.Path().absolute() / 'icenlp' / 'IceNLPCore' / 'bat'

IPFOLDER = ICENLP / 'iceparser'
ICEPARSER = './iceparser.sh'
TAGFOLDER = ICENLP / 'icetagger'
TAGGER = './icetagger.sh'  # TODO change to another tagger, IceStagger or ABLtagger


SKIP_LINES = set(["(META", "(ID-CORPUS", "(ID-LOCAL", "(URL", "(COMMENT"])
SKIP_SEGS = set(["lemma", "exp"])

# Phrases from Greynir schema not included in the general schemas
NOT_INCLUDED = set(["P", "TO"])

# Phrases from Greynir schema not included in the partial general schema
NOT_PARTIAL = set([
	"IP",
	"IP-INF",
	"CP",
	"CP-ADV-ACK",
	"CP-ADV-CAUSE",
	"CP-ADV-COND",
	"CP-ADV-PURP",
	"CP-ADV-TEMP",
	"CP-ADV-CMP",
	"CP-QUE",
	"CP-REL",
	"CP-THT",
	"CP-QUOTE",
	"S0",
	"S0-X",
	"S",
	"S-MAIN",
	"S-HEADING",
	"S-PREFIX"
	"S-QUE",
	])

# Map phrases and leaves in Greynir and IceNLP to the generalized schema
GENERALIZE = {
	# terminals in Greynir
	"no" : "n",
	"kvk" : "n",
	"kk" : "n",
	"hk" : "n",
	"person" : "n",
	"sérnafn" : "n",
	"entity" : "n",
	"fyrirtæki" : "n",
	"gata" : "n",
	"so" : "s",
	"ao" : "a",
	"eo" : "a",
	"fs" : "a",
	"lo" : "l",
	"fn" : "f",
	"pfn" : "f",
	"abfn" : "f",
	"gr" : "g",
	"st" : "c",
	"stt" : "c",
	"nhm" : "c",
	"abbrev" : "k",
	"to" : "t",
	"töl" : "t",
	"tala" : "t",
	"talameðbókstaf" : "t",
	"prósenta" : "t",
	"raðnr" : "t",
	"ártal" : "t",
	"amount" : "t",
	"sequence" : "t",
	"dagsafs" : "a",
	"dagsföst" : "a",
	"tími" : "t",
	"tímapunktur" : "a", # Skoða dæmin
	"tímapunkturafs" : "a",
	"tímapunkturfast" : "a",
	"uh" : "u",
	"myllumerki" : "v",
	"grm" : "p",
	"lén" : "v",
	"notandanafn" : "v",
	"vefslóð" : "v",
	"tölvupóstfang" : "v",
	"sameind" : "m",
	"mælieining" : "t",
	"símanúmer" : "t",
	"kennitala" : "t",
	"vörunúmer" : "t",
	"entity" : "e",
	"foreign" : "e",
	"x" : "x",
	# Non-terminals in Greynir and IceNLP
	"AdvP" : "ADVP",
	"MWE_AdvP" : "ADVP",
	"MWE_AdvP-OBJ" : "ADVP", # Skoða dæmin
	"TIMEX" : "ADVP",
	"InjP" : "ADVP",
	"ADVP" : "ADVP",
	"ADVP-DATE" : "ADVP",
	"ADVP-DATE-ABS" : "ADVP",
	"ADVP-DATE-REL" : "ADVP",
	"ADVP-DIR" : "ADVP",
	"ADVP-DUR-ABS" : "ADVP",
	"ADVP-DUR-REL" : "ADVP",
	"ADVP-DUR-TIME" : "ADVP",
	"ADVP-TIMESTAMP-ABS" : "ADVP",
	"ADVP-TIMESTAMP-REL" : "ADVP",
	"ADVP-TMP-SET" : "ADVP",
	"ADVP-PCL" : "ADVP",
	"ADVP-LOC" : "ADVP",
	"AP" : "ADJP",
	"APs" : "ADJP",
	"AP-SUBJ" : "ADJP-SUBJ",
	"APs-SUBJ" : "ADJP-SUBJ",
	"AP-OBJ" : "ADJP-OBJ",
	"APs-OBJ" : "ADJP-OBJ",
	"AP-IOBJ" : "ADJP-IOBJ",
	"APs-IOBJ" : "ADJP-IOBJ",
	"AP-COMP" : "ADJP-PRD",
	"APs-COMP" : "ADJP-PRD",
	"ADJP" : "ADJP",
	"NPs" : "NP",
	"MWE_AP" : "ADJP",
	"NP-OBJAP" : "NP-ADP",
	"NPs-OBJAP" : "NP-ADP",
	"NP-QUAL" : "NP-POSS",
	"NPs-QUAL" : "NP-POSS",
	"NP-QUAL-SUBJ" : "NP-SUBJ", # Skoða betur
	"NP-COMP" : "NP-PRD",
	"NP-QUAL-COMP" : "NP-COMP", # Skoða betur
	"NPs-COMP" : "NP-PRD",
	"NP-OBJNOM" : "NP",
	"NPs-OBJNOM" : "NP",
	"NP-TIMEX" : "NP",
	"NP" : "NP",
	"NP-SUBJ" : "NP-SUBJ",
	"NPs-SUBJ" : "NP-SUBJ",
	"NP-OBJ" : "NP-OBJ",
	"NPs-OBJ" : "NP-OBJ",
	"NP-QUAL-OBJ" : "NP-OBJ", # Skoða betur
	"NP-IOBJ" : "NP-IOBJ",
	"NPs-IOBJ" : "NP-IOBJ",
	"NP-PRD" : "NP-PRD",
	"NP-POSS" : "NP-POSS",
	"NP-ADP" : "NP-ADP",
	"NP-ES" : "NP",
	"NP-DAT" : "NP",
	"NP-ADDR" : "NP",
	"NP-AGE" : "NP",
	"NP-MEASURE" : "NP",
	"NP-COMPANY" : "NP",
	"NP-PERSON" : "NP",
	"NP-TITLE" : "NP",
	"NP-SOURCE" : "NP",
	"NP-PREFIX" : "NP",
	"NP-EXPLAIN" : "NP",
	"NP-EXCEPT" : "NP",  # Skoða betur
	"MWE_PP" : "PP",
	"PP" : "PP",
	"PP-SUBJ" : "PP", # Skoða betur
	"PP-DIR" : "PP",
	"PP-LOC" : "PP",
	"VPi" : "VP",
	"VPb" : "VP",
	"VPs" : "VP",
	"VPp" : "VP",
	"VPp-COMP" : "VP-PRD",
	"VPg" : "VP",
	"VP?Vn?" : "VP",   # This shouldn't happen
	"VP" : "VP",
	"VP-AUX" : "VP-AUX",
	"SCP" : "C",
	"CP" : "C",
	"MWE_CP" : "C",
	"C" : "C",
	"FRW" : "FOREIGN",
	"FRWs" : "FOREIGN",
	"FOREIGN" : "FOREIGN",

	"IP" : "IP",
	"IP-INF" : "IP",
	"IP-INF-SUBJ" : "IP",
	"IP-INF-OBJ" : "IP",
	"IP-INF-IOBJ" : "IP",
	"IP-INF-PRD" : "IP",
	"CP-ADV" : "CP-ADV",
	"CP-ADV-ACK" : "CP-ADV",
	"CP-ADV-CAUSE" : "CP-ADV",
	"CP-ADV-COND" : "CP-ADV",
	"CP-ADV-CONS" : "CP-ADV",
	"CP-ADV-PURP" : "CP-ADV",
	"CP-ADV-TEMP" : "CP-ADV",
	"CP-ADV-CMP" : "CP-ADV",
	"CP-QUOTE" : "CP",
	"CP-SOURCE" : "CP",
	"CP-QUE" : "CP-QUE",
	"CP-QUE-SUBJ" : "CP-QUE",
	"CP-QUE-OBJ" : "CP-QUE",
	"CP-QUE-IOBJ" : "CP-QUE",
	"CP-QUE-PRD" : "CP-QUE",
	"CP-REL" : "CP-REL",
	"CP-THT" : "CP-THT",
	"CP-THT-SUBJ" : "CP-THT",
	"CP-THT-OBJ" : "CP-THT",
	"CP-THT-IOBJ" : "CP-THT",
	"CP-THT-PRD" : "CP-THT",
	"CP-EXPLAIN" : "CP",
	"S0" : "S0",
	"S0-X" : "S0",
	"S-MAIN" : "S",
	"S-HEADING" : "S",
	"S-PREFIX" : "ADVP",
	"S-QUE" : "S",
	"S-QUOTE" : "S",
	"S-EXPLAIN" : "S",

	"P" : "",
	"TO" : "",
	"FOREIGN" : "",
}

PUNCT = "?!:.,;/+*-\"\'$%&()"

# Get parsed files for each parser
def get_annoparse(infolder, outfolder, insuffix=".txt", outsuffix=".psd", overwrite=False):
	""" Takes text files in a specified folder as input and returns files in another specified folder
		containing parse trees following the Greynir schema """
	for p in infolder.iterdir():
		ptext = p.stem + insuffix
		ptext = infolder / ptext	# Input file
		pout = p.stem + outsuffix
		pout = outfolder / pout		# Output file
		if pout.exists() and not overwrite:
			continue

		command = "annoparse -i {} -o {} -s".format(ptext, pout)
		skil = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).communicate()[0]
		print(skil)

def get_icenlpparse(infolder, outfolder, insuffix=".txt", outsuffix=".inpsd", overwrite=False):
	""" Takes text files in a specified folder as input and returns files in another specified folder
		containing parse trees following the IceParser schema """
	
	origpath = pathlib.Path().absolute()

	# Necessary for IceParser to work correctly
	os.chdir(TAGFOLDER)
	tagsuffix = '.tagged'
	tagfolder = origpath / 'gentag'

	for p in infolder.iterdir():
		ptext = p.stem + insuffix
		ptext = infolder / ptext
		ptag = p.stem + tagsuffix
		ptag = tagfolder / ptag

		if ptag.exists() and not overwrite:
			continue

		command = "{} -i {} -o {} -lf 2 -of 2".format(TAGGER, ptext, ptag)
		skil = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).communicate()[0]
		print(skil)


	# Necessary for IceParser to work correctly
	os.chdir(IPFOLDER)

	for p in infolder.iterdir():
		ptext = p.stem + tagsuffix
		ptext = tagfolder / ptext
		pout = p.stem + outsuffix
		pout = outfolder / pout

		if pout.exists() and not overwrite:
			continue

		command = "{} -i {} -o {} -f -m".format(ICEPARSER, ptext, pout)
		skil = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE).communicate()[0]
		print(skil)

	# Back to original
	os.chdir(origpath)

def get_ipparse(infolder, outfolder, insuffix=".txt", outsuffix=".ippsd", overwrite=False):
	""" Fill this out """
	pass

# Get general parse trees for each parsing schema
def annotald_to_general(infolder, outfolder, insuffix, outsuffix, deep=True, overwrite=False, exclude=False):
	
	for p in infolder.iterdir():
		if p.suffix != insuffix:
			# File has other suffix
			continue

		pin = p.stem + insuffix
		pin = infolder / pin
		pout = p.stem + outsuffix
		pout = outfolder / pout
		

		if pout.exists() and not overwrite:
			continue

		print("Transforming file: {}".format(p.stem+p.suffix))

		# Að mestu eins og readTrees() í annotald.treedrawing
		treetext = pin.read_text()
		treetext = util.scrubText(treetext)
		trees = treetext.strip().split("\n\n")

		outtrees = general_clean(trees, deep, exclude)
		pout.write_text(outtrees)

def icenlp_to_general(infolder, outfolder, insuffix=".inpsd", outsuffix=".inpbr", overwrite=False):
	for p in infolder.iterdir():
		if p.suffix != insuffix:
			# File has other suffix
			continue

		pin = p.stem + insuffix
		pin = infolder / pin
		pout = p.stem + outsuffix
		pout = outfolder / pout

		if pout.exists() and not overwrite:
			continue

		print("Transforming IceParser: {}".format(p.stem))
		treetext = pin.read_text()
		treetext = treetext.replace("\n \n", "\n") # Remove (almost) empty lines
		trees = treetext.strip().split("\n") # One tree per line
		outtrees = general_ipclean(trees)
		pout.write_text(outtrees)

def general_clean(trees, deep=True, exclude=False):
	# Forvinnsla 
	outtrees = "" # All partial trees for file
	text = []
	phrases = Stack()
	numwrongs = 0
	for tree in trees:
		skips = 0
		cleantree = ""
		text = []
		for line in tree.split("\n"):
			if not line:
				continue
			segs = False # Segs found, should skip content of brackets
			# 1. (META, (COMMENT, ... in SKIP_LINES -- skip line altogether
			# 2. Single ( -- extra bracket around tree, won't collect
			# 3. (PP -- collect "(PP" and push one; except if not included
			# 4. (no_kvk_nf_et -- collect "(no_kvk_nf_et" and push one
			# 5. (lemma, (exp_seg, (exp_abbrev -- in SKIP_SEGS, increase numofskipsegs by one. 
			#    Ignore rest of sentence except for )) or more.
			# 6. ) or )))))) -- look at numofskipsegs, otherwise just add
			# 7. word -- single word. Collect in text, until find (lemma
			# 7B. word))) --- If numofskipphrases, check that.
			# 8. (grm -- no lemma here, can mess things up.
			# 9. \) -- escaped parentheses. Opening parentheses, \(, are not a problem. Is the word.
			for item in line.lstrip().split():
				if item.startswith("\\)"):
					item = item.replace("\\)", "&#41;")
				elif item.startswith("\\()") or item.startswith("\\("): 
					# Latter case for unknown tokens
					item = item.replace("\\(", "&#40;")
				if not item:
					continue
				elif item in SKIP_LINES: # Case 1
					break	# Don't collect anything in line
				elif item.startswith("http"): # Case 1
					break # Don't collect anything in line
				elif "(" in item:  # Start new phrase
					if text: # Write before do anything else
						cleantree = cleantree + "_".join(text)
						text = []
					phrase = item.replace("(", "").split("_")[0]  
					if not phrase: # Single (, don't want in cleantree
						skips +=1
						phrases.push("")
						continue					
					if phrase in SKIP_SEGS:
						skips +=1
						segs = True
						phrases.push(phrase)
						continue
					if exclude and phrase == "S0-X":
						pass
					else:
						phrase = GENERALIZE[phrase]
					if not phrase or phrase in NOT_INCLUDED:
						skips +=1
						phrases.push(phrase)
						continue
					if not deep and phrase in NOT_PARTIAL:
						skips +=1
						phrases.push(phrase)
						continue
					phrases.push(phrase)
					cleantree = cleantree + "(" + phrase + " "
				elif ")" in item:
					if segs:
						segs = False
						text = []
					else:
						wordinleaf = item.replace(")", "")
						text.append(wordinleaf)
					brackets = item.count(")")
					bwrite = ""
					for x in range(brackets):
						phrase = phrases.pop()
						if not phrase or phrase in NOT_INCLUDED or phrase in SKIP_SEGS: 
							# Skip corresponding )
							skips -=1
						elif not deep and phrase in NOT_PARTIAL:
							skips -=1
						else:
							bwrite = bwrite + ")"
					cleantree = cleantree + "_".join(text) + bwrite + " "
					text = []
				else:
					text.append(item)

		cleantree = cleantree.rstrip().replace(" )", ")")

		if cleantree.count("(")  != cleantree.count(")"):
			numwrongs +=1
		outtrees = outtrees + cleantree + "\n" 
	return outtrees

def general_ipclean(trees):
	# Forvinnsla 
	outtrees = "" # All partial trees for file
	text = []
	phrases = Stack()
	numwrongs = 0
	for tree in trees:
		skips = 0
		cleantree = ""
		text = [] # Text in each leaf
		next_is_tag = False
		for item in tree.lstrip().split():
			if not item:
				continue
			if item.startswith("\)"):
				item = item.replace("\)", "&#41;")
			elif item.startswith("\("):
				item = item.replace("\(", "&#40;")
			elif "[" in item:  # Byrja nýjan lið
				if text: # Write before do anything else
					cleantree = cleantree + "_".join(text)
					text = []
				phrase = item.replace("[", "").replace("<", "").replace(">", "") 
				if not phrase:  # Empty "[ "! Should be escaped in parsing/tagging
					skips+=1
					continue
				phrase = GENERALIZE[phrase]
				cleantree = cleantree + "(" + phrase + " "
			elif "]" in item:
				wordinleaf = item.replace("]", "")
				if text:
					text.append(wordinleaf)
				if skips < 0:
					skips-=1
					cleantree = cleantree + "_".join(text)
				else:
					cleantree = cleantree + "_".join(text) + ") "
				text = []
			elif next_is_tag:  # Mark fyrir fyrra orð fundið
				if item in PUNCT:
					item = "p"
				cleantree = cleantree + "(" + item[0] + " " + "_".join(text) + ") "
				next_is_tag = False
				text = []
			else:  # Stakt orð fundið
				text.append(item)
				next_is_tag = True

		cleantree = cleantree.rstrip().replace(") )", "))")

		if cleantree.count("(")  != cleantree.count(")"):
			numwrongs +=1
		outtrees = outtrees + cleantree + "\n" 
	return outtrees

def get_results(goldfolder, testfolder, reportfolder, tests, exclude=False):
	evalbpath = pathlib.Path().absolute() / 'EVALB' / 'evalb'
	if not evalbpath.exists:
		print("Evalb cannot be found. Exiting.")
		return

	for pgold in goldfolder.iterdir():
		# (testsuffix, goldsuffix, outsuffix)
		for tri in tests:	
			if pgold.suffix == tri[1]:
				ptest = pgold.stem + tri[0]
				ptest = testfolder / ptest
				pout = pgold.stem + tri[2]
				pout = reportfolder / pout

				if exclude:
					delete_lines(pgold, ptest, goldfolder, testfolder)


				evalbcmd = str(evalbpath) + EVALBCOMMAND + " {} {} > {}".format(pgold, ptest, pout)
				print("Comparing {}\n\t and {}".format(pgold, ptest))
				skil = subprocess.Popen([evalbcmd], shell=True, stdout=subprocess.PIPE).communicate()[0]
				print(skil)

def combine_reports(reportfolder, suffixes, genres, nocat):
	# Bæta við skoðun á setningarhlutverki -- NP-OBJ, ... En þarf sérniðurstöður fyrir það, sérútgáfu af to_brackets...
	numsents = []
	numerrorsents = []
	br = []  # Bracketing recall
	bp = []  # Bracketing precision
	bf = []  # Bracketing F-measure
	cm = []  # Complete match
	ta = []  # Tagging accuracy
	ac = []  # Average crossing
	filenames = []
	filepath = pathlib.Path().absolute() / reportfolder / 'allresults.out'
	singleblob = []
	CM = defaultdict(int)
	CMsingle = defaultdict(int)
	onlygold = list()
	onlyauto = list()
	singleblob.append("Results for each sentence\n")
	# Sækja nauðsynlegar grunnupplýsingar
	for preport in reportfolder.iterdir():
		with preport.open(mode='r') as pin:
			#print(preport)
			filenames.append(preport)
			single = False
			sentid = ""
			singleblob.append("{}\n".format(preport))
			singleblob.append("\tid\tRecall\tPrec.\tTag Acc.  Length\tF1\n")

			while True:
				line = pin.readline()
				#print("A: {}".format(line))
				if line.startswith("  Sent."):
					#print("B: {}".format(line))
					x = pin.readline()
					single = True
					continue
				elif line.startswith("-<1>---"):
					# Starting confusion matrix results
					#print("C: {}".format(line))
					while True:
						terminalline = pin.readline()
						#print("D: {}".format(terminalline))
						if not " " in terminalline:
							# Getting to phrases
							#print("D1: {}".format(terminalline))
							break

						parts = terminalline.split()
						pos1 = parts[4]
						if len(parts) > 6:
							pos2 = parts[10]
						if terminalline.count(" : ") == 2:
							# only one entry, must find out which
							if line.startswith("       "):
								poscm = "_\t{}".format(pos1)
								CM[poscm]+=1
								CMsingle[poscm]+=1
							else:
								poscm = "{}\t_".format(pos1)
								CM[poscm]+=1
								CMsingle[poscm]+=1
						else:
							poscm = "{}\t{}".format(pos1, pos2)
							CM[poscm]+=1
							CMsingle[poscm]+=1
						continue
					goldphrases = []
					autophrases = []
					while True:
						phraseline = pin.readline()
						#print("E: {}".format(phraseline))
						if not " " in phraseline:	
							#diffs = set(goldphrases) ^ set(autophrases)
							onlygold = list([g for g in goldphrases+autophrases if g not in autophrases])
							onlyauto = list([a for a in goldphrases+autophrases if a not in goldphrases])

							"""
							# Comparing gold and auto phrases before the next sentence
							#print("E1: {}".format(terminalline))
							# evalb only details right and wrong phrases
							# We are interested in a more fine-grained analysis
							# Case 1: Both phrases have the same label and same span
							# Case 2: Phrases have same label, wrong but overlapping spans
							# Case 3: Gold has extra phrases
							# Case 4: Auto has extra phrases
							# Case 5: Phrases have the wrong label and the wrong span
							#         but the spans overlap.
							g = iter(goldphrases)
							a = iter(autophrases)
							gp, ap = None, None
							try:
								gp = next(g)
								ap = next(a)
								CM["phrases"] += (len(goldphrases) + len(autophrases))
								while True:
									gspan = set(range(int(gp[0]), int(gp[1]) + 1))
									aspan = set(range(int(ap[0]), int(ap[1]) + 1))
									print("Ber saman: {}\t{}".format(gp, ap))
									glabel = gp[2]
									alabel = ap[2]
									if glabel == alabel:
										if gspan == aspan:
											# Case 1
											phrasecm = "{}\t{}".format(gp[2], ap[2])
											print("\t{}".format(phrasecm))
											CM[phrasecm] += 1
											CMsingle[phrasecm] += 1
											gp, ap = None, None
											gp = next(g)
											ap = next(g)
											continue
										elif gspan & aspan:
											# Case 2
											phrasecm = "{}\t{}".format(gp[2], ap[2])
											print("\t{}".format(phrasecm))
											CM[phrasecm] += 1
											CMsingle[phrasecm] += 1
											gp, ap = None, None
											gp = next(g)
											ap = next(g)
											continue
										#	pass
									if int(gp[1]) + 1 < int(ap[1]):
										# Case 3
										phrasecm = "{}\t_".format(gp[2])
										print("\t{}".format(phrasecm))
										CM[phrasecm] += 1
										CMsingle[phrasecm] += 1
										gp = None
										gp = next(g)
									elif int(ap[1]) + 1 < int(gp[1]):
										# Case 4
										phrasecm = "_\t{}".format(ap[2])
										print("\t{}".format(phrasecm))
										CM[phrasecm] += 1
										CMsingle[phrasecm] += 1
										ap = None
										ap = next(a)
									else:
										# Case 5, mostly
										phrasecm = "{}\t_".format(gp[2])
										print("\t{}".format(phrasecm))
										CM[phrasecm] += 1
										CMsingle[phrasecm] += 1
										phrasecm = "_\t{}".format(ap[2])
										print("\t{}".format(phrasecm))
										CM[phrasecm] += 1
										CMsingle[phrasecm] += 1
										gp = None
										ap = None
										gp = next(g)
										ap = next(a)
										continue
							except StopIteration:
								pass
							#print("E2")
							if gp:
								# Process rest of g as Case 3
								while gp is not None:
									phrasecm = "{}\t_".format(gp[2])
									print("\t{}".format(phrasecm))
									CM[phrasecm] += 1
									CMsingle[phrasecm] += 1
									gp = next(g, None)
							if ap:
								# Process rest of a as Case 4
								while ap is not None:
									phrasecm = "_\t{}".format(ap[2])
									print("\t{}".format(phrasecm))
									CM[phrasecm] += 1
									CMsingle[phrasecm] += 1
									ap = next(a, None)
							"""
							break
						parts = phraseline.split()
						phrase1 = parts[6]+"\t"+parts[4]+"-"+parts[5]
						#parts[4:7]
						if len(parts) > 9:
							phrase2 = parts[13]+"\t"+parts[11]+"-"+parts[12]
						if phraseline.count(" : ") == 2:
							# Only one entry, must find out which
							if line.startswith("       "):
								autophrases.append(phrase1)
							else:
								goldphrases.append(phrase1)
						else:
							goldphrases.append(phrase1)
							autophrases.append(phrase2)
						continue
				if line.count("=") == 8 or single:
					# Results for next sentence coming
					#print("F: {}".format(line))
					sentsultsline = pin.readline()
					#print("F1: {}".format(sentsultsline))
					single = False
					if  "========" in sentsultsline:
						# Starting summary
						while True:
							summline = pin.readline()
							#print("G: {}".format(summline))
							#print(summline)
							if summline.startswith("Number of sentence "):
								numsents.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Number of Error sentence "):
								numerrorsents.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Bracketing Recall "):
								br.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Bracketing Precision "):
								bp.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Bracketing FMeasure "):
								if "nan" in summline.split(" ")[-1]:
									bf.append(0.0)
								else:	
									bf.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Complete match "):
								cm.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Average crossing "):
								ac.append(float(summline.split(" ")[-1]))
							elif summline.startswith("Tagging accuracy "):
								ta.append(float(summline.split(" ")[-1]))
								break # No information needed after this
							continue
					else:
						#print("H: {}".format(sentsultsline))

						sults = sentsultsline.split()
						sentid = sults[0]
						sentlength = float(sults[1])
						sentrecall = float(sults[3])
						sentprec = float(sults[4])
						senttags = float(sults[10])
						warning = ""
						f1 = 0.0
						if sentprec + sentrecall > 0.0:
							f1 = 2 * sentprec * sentrecall / (sentprec + sentrecall)
						if f1 < 20.0:
							warning = "WARNING"

						singleblob.append(f"\t{sentid}\t{sentrecall:1.2f}\t{sentprec:1.2f}\t{senttags:1.2f}\t  {sentlength:.2f}\t\t{f1:1.2f}\t{warning}\n")
						for og, oa in list(itertools.zip_longest(onlygold, onlyauto, fillvalue="    ")):
							singleblob.append(f"\t\t{og:15}{oa:15}\n")
						onlygold, onlyauto = list(), list()
						#cmblob = list( ["\t\t{}\t{}\n".format(key, CMsingle[key]) for key in CMsingle ] )
						#CMsingle = defaultdict(int)
						#singleblob = singleblob + cmblob
						#for key in CMsingle:
						#	singleblob.append("{}\t{}\n".format(key, CMsingle[key]))
						#break
				elif line == "":
					# end of file
					break
				continue

	# Birta réttar upplýsingar
	# Geri ráð fyrir að það séu 10 setningar í hverju skjali
	# til að forðast of lágar tölur sem hverfa
	textblob = []
	for suff in suffixes:
		numfilesoverall, numsentsoverall, numerrorsentsoverall = 0, 0.0, 0.0
		broverall, bpoverall, bfoverall, cmoverall, acoverall, taoverall = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
		textblob.append("\n\n")
		for genre in genres:
			fileid = genre+suff
			filestrings = []
			numfiles = 0
			numsentsall, numerrorsentsall = 0.0, 0.0
			brall, bpall, bfall, cmall, acall, taall = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
			allnums = zip(filenames, numsents, numerrorsents, br, bp, bf, cm, ac, ta)
			for filenow, numsentsnow, numerrorsentsnow, brnow, bpnow, bfnow, cmnow, acnow, tanow in allnums:
				if filenow.suffix != suff:
					continue
				if not filenow.stem.startswith(genre):
					continue
				filestrings.append(str(filenow))
				numfiles+=1
				numsentsall+=numsentsnow
				numerrorsentsall+=numerrorsentsnow
				brall+=brnow
				bpall+=bpnow
				bfall+=bfnow
				cmall+=cmnow
				acall+=acnow
				taall+=tanow

			#filepath = pathlib.Path().absolute() / reportfolder / fileid
			numfilesoverall+=numfiles
			numsentsoverall+=numsentsall
			numerrorsentsoverall+=numerrorsentsall
			broverall+=brall
			bpoverall+=bpall
			bfoverall+=bfall
			cmoverall+=cmall
			acoverall+=acall
			taoverall+=taall
			if not nocat: # Skip results by category
				textblob.append("=== {} ===\n".format(fileid))
				if numfiles == 0:
					textblob.append("Engin skjöl í flokki\n")
					continue

				textblob.append("Fjöldi setninga:{}\n".format(numsentsall))
				textblob.append("Fjöldi villusetninga:{}\n".format(numerrorsentsall))
				textblob.append("Recall:{:.2f}\n".format(brall/numfiles))
				textblob.append("Precision:{:.2f}\n".format(bpall/numfiles))
				textblob.append("Fskor:{:.2f}\n".format(bfall/numfiles))
				textblob.append("Alveg eins:{:.2f}\n".format(cmall/numfiles))
				textblob.append("Average crossing: {:.2f}\n".format(acall/numfiles))
				textblob.append("Tagging accuracy:{:.2f}\n\n\t".format(taall/numfiles))
				#textblob.append("\n\t".join(filestrings))
				textblob.append("\n\n")

		textblob.append("=== Heildin{} ===\n".format(suff))

		if numfilesoverall == 0:
			textblob.append("Engin skjöl\n")
			

		textblob.append("Fjöldi setninga:{}\n".format(numsentsoverall))
		textblob.append("Fjöldi villusetninga:{}\n".format(numerrorsentsoverall))
		if broverall == 0.0:
			textblob.append("Recall: N/A\n")
		else:
			textblob.append("Recall: {:.2f}\n".format(broverall/numfilesoverall))
		if bpoverall == 0.0:
			textblob.append("Precision: N/A\n")
		else:
			textblob.append("Precision: {:.2f}\n".format(bpoverall/numfilesoverall))
		if bfoverall == 0.0:
			textblob.append("Fskor: N/A\n")
		else:
			textblob.append("Fskor: {:.2f}\n".format(bfoverall/numfilesoverall))
		if cmoverall == 0.0:
			textblob.append("Alveg eins: N/A\n")
		else:
			textblob.append("Alveg eins: {:.2f}\n".format(cmoverall/numfilesoverall))
		if acoverall == 0.0:
			textblob.append("Avg crossing: N/A\n")
		else:
			textblob.append("Avg crossing: {:.2f}\n".format(acoverall/numfilesoverall))
		if taoverall == 0.0:
			textblob.append("Tag accuracy: N/A\n")
		else:
			textblob.append("Tag accuracy: {:.2f}\n".format(taoverall/numfilesoverall))



	print("Writing overall report")
	textblob = textblob + ["\n\n"] + singleblob
	for key in CM:
		textblob.append("{}\t{}\n".format(key, CM[key]))
	filepath.write_text("".join(textblob))


# Not needed in ParsingTestPipe, only if text files are needed from bracketed files.
def br_to_txt(infolder, outfolder, insuffix=".dbr", outsuffix=".txt", overwrite=False):
	for p in infolder.iterdir():
		if p.suffix != insuffix:
			continue

		pin = p.stem + insuffix
		pin = infolder / pin
		pout = p.stem + outsuffix
		pout = outfolder / pout
		
		if pout.exists() and not overwrite:
			continue

		print("Transforming file: {}".format(p.stem+p.suffix))

		brtext = pin.read_text()
		txt = []
		for line in brtext.split("\n"):
			clean = []
			if not line:
				continue
			for item in line.lstrip().split():
				if "(" in item:
					continue
				elif ")" in item:
					item = item.replace(")", "")

				for each in item.split("_"):
					clean.append(each)
			txt.append(" ".join(clean))

		pout.write_text("\n".join(txt))

def delete_lines(pgold, ptest, goldfolder, testfolder):
	""" Deletes lines containing S0-X in brackets so they are excluded from evaluation """
	skipped = []
	i = 0
	fakegold = pgold.stem + '.bak'
	fakegold = goldfolder / fakegold
	faketest = ptest.stem + '.bak'
	faketest = testfolder / faketest
	with open(pgold, 'r') as orgfile, open(fakegold, 'w') as fakefile:
		for line in orgfile:
			if "S0-X" in line:
				skipped.append(i)
			else:
				fakefile.write(line)
			i +=1

		if skipped:
			with open(ptest, 'r') as orgfile, open(faketest, 'w') as fakefile:
				j = 0
				for line in orgfile:
					if j not in skipped:
						fakefile.write(line)
					j +=1

			os.remove(pgold)
			os.rename(fakegold, pgold)
			os.remove(ptest)
			os.rename(faketest, ptest)
		else:
			os.remove(fakegold)



class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)


if __name__ == "__main__":
	print(" ")
