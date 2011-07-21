'''
Script to automatically generate documentation stubs for schemes

Author: Gary Belvin
'''
import os, re
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
   dir = "schemes"
   for m in modules:
       out += dir + "/" + m + '\n'
   return out

def gen_doc_stub(module):
   out = \
   """%s
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
   print("Modules  =>", mods)
   print("TOC      =>",gen_toc(mods))
   print("module   =>", mods[1])
   print(gen_doc_stub(mods[1]))

  


