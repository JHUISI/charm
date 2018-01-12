#!/usr/bin/python

# create_deb.py
# Creates a .deb binary package for charm based on the current install.
# This script requires that charm deps are already installed.
# The script must be run as root.
# See INSTALL document for more details.

from __future__ import print_function
import glob
import os
import shutil
import subprocess
import sys

# globals
# version number from config.mk
CHARM_VERSION = "0.50"

# python version to use - python or python3
if sys.version_info[0] < 3:
    PYTHON_VERSION = "python"
else:
    PYTHON_VERSION = "python3"

# move to root of repository
install_dir = os.getcwd()
os.chdir("../..")
root_dir = os.getcwd()

# back up original setup.py before modification
shutil.copy2("setup.py", "setup.py.bak")

# perform subsitution
with open("setup.py.bak", "r") as f:
    data = f.readlines()

for i in range(0, len(data)):
    if "inc_dirs = " in data[i]:
        data[i] = "inc_dirs = []\n"
    elif "runtime_library_dirs = " in data[i]:
        data[i] = "runtime_library_dirs = []\n"
        data[i+1] = "\n"
    elif "library_dirs = " in data[i]:
        data[i] = "library_dirs = []\n"

with open("setup.py", "w") as f:
    f.writelines(data)

# perform source packaging
sdist_dsc = (PYTHON_VERSION + 
        " setup.py --command-packages=stdeb.command sdist_dsc")
subprocess.check_call(sdist_dsc, shell=True)

# modify debian rules to ignore pbc dependency 
os.chdir("deb_dist/charm-crypto-" + CHARM_VERSION)
added_rule = ("override_dh_shlibdeps:\n\tdh_shlibdeps " +
    "--dpkg-shlibdeps-params=--ignore-missing-info\n\n\n")
with open("debian/rules", "a") as f:
    f.write(added_rule)

# build the .deb
build_deb = "sudo dpkg-buildpackage -rfakeroot -uc -us"
subprocess.check_call(build_deb, shell=True)

# move installer
os.chdir("..")
for deb in glob.glob("*.deb"):
    shutil.copy2(deb, install_dir + "/" + deb)

# restore backup of setup.py
os.chdir(root_dir)
os.rename("setup.py.bak", "setup.py")

