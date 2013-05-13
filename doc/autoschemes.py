'''
Script to automatically generate documentation stubs for schemes, toolbox and test code

Author: Gary Belvin
'''
import os, re
import config

skipList = config.skip_list

def find_modules(path=".", excludeTests=True):
    if type(path) == str:
       path = [path]
    modules = list()
    for this_path in path: 
        for filename in os.listdir(this_path):
            #print("file: ", filename)
            if re.match("^[^_][\w]+\.py$", filename):
               module = filename[:-3]
               modules.append(module)

    #Exclude unit tests
    if excludeTests: modules = [mod for mod in modules if not re.match(".*_test$", mod)]
    try:
        for i in skipList:
            modules.remove(i)    
    except:
        pass
    modules.sort(key=str.lower)
    #print("Modules selected =>", modules)
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

def gen_toc2(keyword, data):
   scheme_list = ""
   #mods, rel_mod_dir = data
   for k,mods in data.items():
       for m in mods:
           rel_mod_dir = k
           scheme_list += "   " + rel_mod_dir + m + '\n'
   #for m in modules:

   replacement=\
""".. begin_%s
.. toctree::
   :maxdepth: 1

%s
.. end_%s""" % (keyword, scheme_list, keyword)
   #print("Result: ", repr(replacement))
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

def replace_toc2(thefile, keyword, data): #modules, rel_mod_dir):
   pattern = "\.\. begin_%s.*\.\. end_%s" % (keyword, keyword)
#   mods, rel_mod_dir = data 
   replacement= gen_toc2(keyword, data)

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
 
def auto_add_rst(modules, rstdir="", create=False):
   #Create files for undocumented modules
   if create: 
       if not os.path.exists(rstdir):
          os.makedirs(rstdir)
   for m in modules:
       #print("m :=>", m)
       #print("rstdir :=>", rstdir)
       #only create stubs if the scheme hasn't already been documented
       rstpath = rstdir + m + ".rst"
       if not os.path.isfile(rstpath):
           with open(rstpath, mode='w',  encoding='utf-8') as f:
               print("Writing new file ", rstpath)
               f.write(gen_doc_stub(m))

if __name__ == "__main__": 
   #Auto add new schemes
   data = {}
   mods = list()
   rel_path = '../'
   slash = '/'
   mod_list = [config.scheme_path, config.abenc_path, config.pkenc_path, config.pksig_path]
   for p in mod_list:
       mods.append( find_modules(rel_path + p) )
   for p in range(len(mod_list)):
       data[ mod_list[p] + slash] =  mods[ p ]

   for k,m in data.items():
       auto_add_rst(m, 'source/' + k, True)      
   replace_toc2('source/schemes.rst', 'auto_scheme_list',  data) #) mods, config.scheme_path + '/')
   
   #Auto add toolbox classes
   print("Adding: ", config.toolbox_path)
   mods = find_modules(config.toolbox_path)
   auto_add_rst(mods, 'source/toolbox/', True)
   replace_toc('source/toolbox.rst', 'auto_toolbox_list', mods, 'toolbox/')

   #Auo add test case code 
   print("Adding: ", config.test_path + "/schemes")
   mods = find_modules(config.test_path + "/schemes", excludeTests=False)
   auto_add_rst(mods, 'source/test/', True)
   replace_toc('source/test_schemes.rst', 'auto_test_schemes_list', mods, 'test/')
  
   print("Adding: ", config.test_path + "/toolbox")
   mods = find_modules(config.test_path + "/toolbox", excludeTests=False)
   auto_add_rst(mods, 'source/test/', True)
   replace_toc('source/test_toolbox.rst', 'auto_test_toolbox_list', mods, 'test/')
