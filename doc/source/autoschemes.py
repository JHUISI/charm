'''
Script to automatically generate documentation stubs for schemes

Author: Gary Belvin
'''
import os, re

rstschemesdir = "schemes"

def find_modules(path="."):
    modules = set()
    for filename in os.listdir(path):
        if re.match("^[^_][\w]+\.py$", filename):
            module = filename[:-3]
            modules.add(module)

    #Exclude unit tests
    modules = [mod for mod in modules if not re.match(".*_test$", mod)]
    return modules

def gen_toc(modules):
   out = ""
   for m in modules:
       out += rstschemesdir + "/" + m + '\n'
   return out

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
 

if __name__ == "__main__": 
   mods = find_modules("../../schemes/")
   #Create files for undocumented modules
   for m in mods:
       #only create stubs if the scheme hasn't already been documented
       rstpath = rstschemesdir + '/' + m + ".rst"
       if not os.path.isfile(rstpath):
           with open(rstpath, mode='w',  encoding='utf-8') as f:
               print("Writing new file ", rstpath)
               f.write(gen_doc_stub(m))
           
   
   #Add modules to main table of contents
   
   
   #print("Modules  =>", mods)
   #print("TOC      =>",gen_toc(mods))
   #print("module   =>", mods[1])
   #print(gen_doc_stub(mods[1]))

  


