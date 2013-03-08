import sys

dir_above = '../'
sdl_pkg = '../sdlparser'
cg_pkg = '../codegen'

if dir_above not in sys.path:
   sys.path.append(dir_above)
if sdl_pkg not in sys.path:
   sys.path.append(sdl_pkg)
if cg_pkg not in sys.path:
   sys.path.append(cg_pkg)
