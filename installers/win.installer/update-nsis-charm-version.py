#!/usr/bin/env python

# The following script will use file io to upate the constant variable VERSION in the NSIS installer script.
# Note that this is probably an easy thing to-do in the script itself... eventually.

# TODO: Update charm.pth with latest version.

import fileinput, sys, re

fver = open('../../VERSION', 'r')
pattern = '!define PRODUCT_VERSION*'
compiled = re.compile(pattern)

for versionLine in fver:
    replacement_string = '!define PRODUCT_VERSION "'+versionLine+'"\n'
    for line in fileinput.input('charm-exe-script-ex.nsi', inplace=1):
        if compiled.search(line):
            newline = line.replace(line, replacement_string)
            sys.stdout.write(newline)
        else:
            sys.stdout.write(line)

fver.close()
