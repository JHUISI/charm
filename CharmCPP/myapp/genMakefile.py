import os, sys
import datetime

YES = "yes"
makefile = """
# Auto-generated makefile on %s
prefix := %s
CXX := %s
CXXFLAGS := %s

INCLUDES := -I. -I.. -I../builtin -I%s %s

NAME := %s
OBJECTS := $(NAME).o %s
LIB  := %s

.PHONY: $(NAME)
$(NAME): $(OBJECTS)
\t$(CXX) $(CXXFLAGS) $(INCLUDES) $(OBJECTS) $(LIB) -o $(NAME)

%s
\t$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
\trm -f *.o $(NAME)
"""

def ReadConfig(file):
    f = open(file, 'r')
    lines = f.read().split('\n')   
    config_key = {}
    for e in lines:
        if e.find('=') != -1:
           eqPos = e.find('=')
           config_key[ e[0:eqPos] ] = e[eqPos+1:] 
    f.close()
    return config_key

def buildMakefile(config_file, cppFiles, makefileName):
    options = ReadConfig(config_file)
    timestamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    cppFileName = cppFiles[0].strip(".cpp") # first will be used as target name as well
    charmLib = options['CHARM_LIB'][3:]
    if(options['BUILD_MIRACL'] == YES):
        charmLibOpt = "-l" + charmLib
        localPathToHeaders = "-I../miracl"
    elif(options['BUILD_RELIC'] == YES):
        charmLibOpt = "-l" + charmLib + " -lrelic"
        localPathToHeaders = "-I../relic"
    else:
        sys.exit("Unrecognized crypto library to build.")
        
    cmd = "%.o: %.cpp"
    if len(cppFiles) > 1:
        cppFileName1 = cppFiles[1].strip(".cpp") + ".o" # to specify object file
        makefileStr = makefile % (timestamp, options['prefix'], options['CXX'], options['CXXFLAGS'], options['incdir'], localPathToHeaders, cppFileName, cppFileName1, charmLibOpt, cmd)
    else:
        makefileStr = makefile % (timestamp, options['prefix'], options['CXX'], options['CXXFLAGS'], options['incdir'], localPathToHeaders, cppFileName, "", charmLibOpt, cmd)        
    print(makefileStr)
    f = open(makefileName, 'w')
    f.write(makefileStr)
    f.close()
    return

if __name__ == "__main__":
    print(sys.argv[1:])
    if(len(sys.argv) < 4):
        print("Insufficient arguments!")
        sys.exit("\tpython %s [ path to config ] [ makefile name ] [ C++ files in order ]" % sys.argv[0])
    config = sys.argv[1]
    makefileName = sys.argv[2]
    if "Makefile" not in makefileName: sys.exit("Did you forget to specify Makefile filename?")
    file = sys.argv[3:]
    print("C++ files: ", file)
    #buildMakefile("../config.mk", "TestCharm.cpp", "MakefileTmp")
    buildMakefile(config, file, makefileName)
    os.system("make -f %s" % makefileName)
    
    
