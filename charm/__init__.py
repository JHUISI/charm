import sys,distutils.sysconfig

# dependency for pairing, integer and ecc mods
import charm.benchmark

# get the path to site-packages for operating system
path_to_charm = distutils.sysconfig.get_python_lib()

# add 'install' package dest to our path 
sys.path.append(path_to_charm + "/charm/")

# now python can easily find our modules

