# ParsingTestPipe
Parsing test pipeline for different parsing schemas.

## Contents
**helpers.py**: Helper functions for the test pipeline

**corpusmanager.py**: Main test pipeline. 
+ Creates original automatically parsed version of hand-annotated corpora
+ Retrieves automatically parsed versions of text files from Greynir and IceParser
+ Transforms parsed files, both gold and files to be tested, from Greynir schema and IceParser schema to a bracketed form for evalb
+ Sends bracketed test and gold files to evalb and combines reports

**test_corpus**: Contains the test corpora.

+ **brackets**: Bracketed form of gold files.
+ **genpsd**: Parsed files. Created at runtime by Greynir (.psd) and IceParser (.ippsd). 
+ **gentag**: Tagged files. Created at runtime by IceParser (.tagged).
+ **handpsd**: Hand-annotated files in the deep general schema (.dgld) and the partial general schema (.pdgld).
+ **reports**: Reports from evalb for each gold standard file. Contains results for Greynir in the deep schema (.grdout) and the partial schema (.grpout), and IceParser in the partial schema (.ippout). Created at runtime. *overallresults.out* contains results both overall for each parser and divided by text genre.
+ **testfiles**: Bracketed form of automatically parsed files to be tested, both from Greynir in the deep schema (.grdbr), and IceParser in the partial schema (.ippbr). Created at runtime.

## Dependencies
The pipeline assumes [evalb](https://nlp.cs.nyu.edu/evalb/) is in the folder ParsingTestPipe/EVALB, and [IceNLP](https://github.com/hrafnl/icenlp) is in the folder ParsingTestPipe/icenlp.

[GreynirPackage](https://github.com/mideind/GreynirPackage) needs to be installed.

## Running the software

 To run the tests, run:
```
    $ python eval.py
```
