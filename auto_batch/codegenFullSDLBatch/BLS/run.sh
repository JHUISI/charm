#!/bin/bash

python generateBLSmsmt.py -g 10 10 100 test validDict invalidDict

python generateBLSmsmt.py -b validDict batch.dat indiv.dat 

