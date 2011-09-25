import sys,distutils.sysconfig
import platform

install_system=platform.system()

if install_system == 'Darwin':
   # get the path to site-packages for operating system
   path_to_charm = distutils.sysconfig.get_python_lib()
   # add 'install' package dest to our path 
elif install_system == 'Windows':
	path_to_charm = distutils.sysconfig.get_python_lib()
elif install_system == 'Linux':
   dist = platform.linux_distribution()[0]
   if dist == 'Ubuntu' or 'LinuxMint':
      path_to_charm = distutils.sysconfig.get_python_lib(1, 1, '/usr/local') + "/dist-packages"
   elif dist == 'Fedora':
      path_to_charm = distutils.sysconfig.get_python_lib(1, 1, '/usr') + "/site-packages"
   #print("python path =>", path_to_charm)
else:
   print("Installing on", install_system)
   
sys.path.append(path_to_charm + "/charm/")
# now python can easily find our modules
# dependency for pairing, integer and ecc mods
import charm.benchmark
