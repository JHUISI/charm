#!/bin/sh

# Charm-Crypto v0.60 macOS Installer Build Script
# Supports Python 3.9+ (Python 2.7 support has been dropped)

# Homebrew Python location (recommended).
./configure.sh --enable-darwin --python=/opt/homebrew/bin/python3; sudo make build; sudo make install; sudo rm config.mk

# Python.org installer location (Intel/Universal).
./configure.sh --enable-darwin --python=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12; sudo make build; sudo make install; sudo rm config.mk
./configure.sh --enable-darwin --python=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11; sudo make build; sudo make install; sudo rm config.mk
./configure.sh --enable-darwin --python=/Library/Frameworks/Python.framework/Versions/3.10/bin/python3.10; sudo make build; sudo make install; sudo rm config.mk
./configure.sh --enable-darwin --python=/Library/Frameworks/Python.framework/Versions/3.9/bin/python3.9; sudo make build; sudo make install; sudo rm config.mk

# MacPorts Python location (alternative).
# ./configure.sh --enable-darwin --python=/opt/local/bin/python3.12; sudo make build; sudo make install; sudo rm config.mk

# System Python (macOS Sonoma+).
# ./configure.sh --enable-darwin --python=/usr/bin/python3; sudo make build; sudo make install; sudo rm config.mk
