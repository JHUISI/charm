#!/bin/sh

# Python Mac Ports location.
./configure.sh --enable-darwin --python=/opt/local/bin/python3.2; sudo make build; sudo make install; sudo rm config.mk
./configure.sh --enable-darwin --python=/opt/local/bin/python2.7; sudo make build; sudo make install; sudo rm config.mk

# Python installers location.
./configure.sh --enable-darwin --python=/Library/Frameworks/Python.framework/Versions/3.2/bin/python3.2; sudo make build; sudo make install; sudo rm config.mk
./configure.sh --enable-darwin --python=/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7; sudo make build; sudo make install; sudo rm config.mk


# Python Lion 2.7 location.
./configure.sh --enable-darwin --python=/usr/bin/python2.7; sudo make build; sudo make install; sudo rm config.mk



# sudo /Library/Frameworks/Python.framework/Versions/3.2/bin/python3.2 setup.py build build_ext -L/usr/local/lib -I/usr/local/include
