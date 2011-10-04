'''
Script to automatically generate documentation stubs for schemes

Author: Gary Belvin
'''
import os, re

skipList = ['ake_ecmqv', 'pksig_rsa_hw09', 'bls04']

def find_modules(path="."):
    modules = list()
    for filename in os.listdir(path):
        if re.match("^[^_][\w]+\.py$", filename):
            module = filename[:-3]
            modules.append(module)

    #Exclude unit tests
    modules = [mod for mod in modules if not re.match(".*_test$", mod)]
    modules = [mod for mod in modules if not re.match("batch.*", mod)]
    modules = [mod for mod in modules if not re.match("bench.*", mod)]
    try:
        for i in skipList:
            modules.remove(i)    
    except:
        pass
    modules.sort(key=str.lower)
    print("Modules selected =>", modules)
    return modules

def gen_toc(modules, keyword, rel_mod_dir=""):
   scheme_list = ""
   for m in modules:
       scheme_list += "   " + rel_mod_dir + m + '\n'

   replacement=\
""".. begin_%s
.. toctree::
   :maxdepth: 1

%s
.. end_%s""" % (keyword, scheme_list, keyword)
   return replacement

def replace_toc(thefile, keyword, modules, rel_mod_dir):
   pattern = "\.\. begin_%s.*\.\. end_%s" % (keyword, keyword)
   replacement= gen_toc(mods, keyword, rel_mod_dir)

   index_contents = ""
   with open(thefile, mode='r', encoding='utf-8') as index:
      index_contents = index.read()

   new_contents = re.sub(pattern, replacement, index_contents, flags=re.S)
   with open(thefile, mode='w', encoding='utf-8') as newindex:
      newindex.write(new_contents)


def gen_doc_stub(module):
   out ="""
%s
=========================================
.. automodule:: %s
    :show-inheritance:
    :members:
    :undoc-members:
""" %(module, module)
   return out
 
def auto_add_rst(modules, rstdir=""):
   #Create files for undocumented modules
   for m in mods:
       #only create stubs if the scheme hasn't already been documented
       rstpath = rstdir + m + ".rst"
       if not os.path.isfile(rstpath):
           with open(rstpath, mode='w',  encoding='utf-8') as f:
               print("Writing new file ", rstpath)
               f.write(gen_doc_stub(m))


if __name__ == "__main__": 
   #Auto add new schemes
   mods = find_modules('../schemes')
   auto_add_rst(mods, 'source/schemes/')        
   replace_toc('source/schemes.rst', 'auto_scheme_list', mods, 'schemes/')
   
   #Auto add toolbox classes
   mods = find_modules('../toolbox')
   auto_add_rst(mods, 'source/toolbox/')
   replace_toc('source/toolbox.rst', 'auto_toolbox_list', mods, 'toolbox/')

  
