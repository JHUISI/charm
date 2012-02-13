#!/bin/sh

# A simple script to exhaustively search for python. 
# As long as the interpreter is found once than this
# will exit successfully.  Else kill the installer.

# Minimum spec is 2.7, the installer can handle the rest 
# through requirement scripts.

if  [ -d /opt/local/Library/Frameworks/Python.framework/Versions/2.7/ ]|| \ 
    [ -d /opt/local/Library/Frameworks/Python.framework/Versions/3.2/ ]|| \
    [ -d /Library/Frameworks/Python.framework/Versions/2.7/           ]|| \ 
    [ -d /Library/Frameworks/Python.framework/Versions/3.2/           ]|| \
    [ -d /Library/Python/2.7/ ]; then
    exit 1
fi 
exit 0
