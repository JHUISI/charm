#!/bin/bash

python generateCHCHHESSmsmt.py -g 100 10 100 test validDict invalidDict

python generateCHCHHESSmsmt.py -b validDict batch.dat indiv.dat 

