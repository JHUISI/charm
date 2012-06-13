#!/bin/bash
source ../bin/activate
for file in `find schemes | grep -v \.pyc | grep -v \.swp | grep -v \.swo | grep \.py` #try and make sure we only test python files
    do
        if [ -f $file ] #is it a file?
        then
            echo $file
            python -m doctest $file
        fi
    done
