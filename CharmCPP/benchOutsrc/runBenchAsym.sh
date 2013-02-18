#!/bin/bash

set -x
# all the asymmetric tests

python genMakefile.py ../config.mk MakefileWATERS TestWATERS.cpp benchWATERS.cpp

python genMakefile.py ../config.mk MakefileBSW TestBSWOut.cpp benchBSWOut.cpp

python genMakefile.py ../config.mk MakefileLW TestLWOut.cpp benchLWOut.cpp

python genMakefile.py ../config.mk MakefileCKRS TestCKRSOut.cpp benchCKRSOut.cpp

python genMakefile.py ../config.mk MakefileHIBE TestHIBEOut.cpp benchHIBEOut.cpp

#python genMakefile.py ../config.mk MakefileHVE TestHVEOut.cpp benchHVEOut.cpp

python genMakefile.py ../config.mk MakefileSW TestSWOut.cpp benchSWOut.cpp

# dfa test 
#python genMakefile.py ../config.mk MakefileDFA TestDFAOut.cpp benchDFAOut.cpp


./TestWATERS 100 100 fixed

./TestBSWOut 100 100 fixed

./TestLWOut 100 100 fixed

./TestCKRSOut 100 100 fixed

./TestHIBEOut 100 100 fixed

./TestSWOut 100 100 fixed

#./TestHVEOut #100 100 fixed
set +x
