'''
Script to automatically generate documentation stubs for schemes

Author: Gary Belvin
'''
import os, re


rstschemesdir = "source/schemes"
indexfile     = "source/index.rst"
indexrelschemes= "schemes"
schemesdir    = "../schemes/"

def find_modules(path="."):
    modules = set()
    for filename in os.listdir(path):
        if re.match("^[^_][\w]+\.py$", filename):
            module = filename[:-3]
            modules.add(module)

    #Exclude unit tests
    modules = [mod for mod in modules if not re.match(".*_test$", mod)]
    modules.sort()
    return modules

def gen_toc(modules):
   scheme_list = ""
   for m in modules:
       scheme_list += "   " + indexrelschemes + "/" + m + '\n'

   replacement=""".. begin_auto_scheme_list
.. toctree::
   :maxdepth: 1

%s
.. end_auto_scheme_list""" % scheme_list
   return replacement

def gen_doc_stub(module):
   out ="""
%s
=========================================
.. todo::
   Document %s

.. automodule:: %s
    :show-inheritance:
    :synopsis:
    :members:
""" %(module, module, module)
   return out
 
def auto_add_scheme_rst(modules):
   #Create files for undocumented modules
   for m in mods:
       #only create stubs if the scheme hasn't already been documented
       rstpath = rstschemesdir + '/' + m + ".rst"
       if not os.path.isfile(rstpath):
           with open(rstpath, mode='w',  encoding='utf-8') as f:
               print("Writing new file ", rstpath)
               f.write(gen_doc_stub(m))


if __name__ == "__main__": 
   mods = find_modules(schemesdir)
   auto_add_scheme_rst(mods)        
   
   #Add modules to main table of contents
   pattern = "\.\. begin_auto_scheme_list.*\.\. end_auto_scheme_list"
   replacement= gen_toc(mods)

   index_contents = ""
   with open(indexfile, mode='r', encoding='utf-8') as index:
      index_contents = index.read()
   
   new_contents = re.sub(pattern, replacement, index_contents, flags=re.S)
   with open(indexfile, mode='w', encoding='utf-8') as newindex:
      newindex.write(new_contents)

   
   #print("Modules  =>", mods)
   #print("TOC      =>",gen_toc(mods))
   #print("module   =>", mods[1])
   #print(gen_doc_stub(mods[1]))

  


