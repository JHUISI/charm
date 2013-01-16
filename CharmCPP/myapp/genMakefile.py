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
OBJECTS := $(NAME).o
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

def buildMakefile(config_file, cppFile, makefileName):
    options = ReadConfig(config_file)
    timestamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    cppFileName = cppFile.strip(".cpp")
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
    makefileStr = makefile % (timestamp, options['prefix'], options['CXX'], options['CXXFLAGS'], options['incdir'], localPathToHeaders, cppFileName, charmLibOpt, cmd)
    print(makefileStr)
    f = open(makefileName, 'w')
    f.write(makefileStr)
    f.close()
    return

if __name__ == "__main__":
    print(sys.argv[1:])
    if(len(sys.argv) != 4):
        print("Insufficient arguments!")
        sys.exit("\tpython %s [ path to config ] [ C++ filename ] [ optional: makefile name ]" % sys.argv[0])
    config = sys.argv[1]
    file = sys.argv[2]
    makefileName = sys.argv[3]
    #buildMakefile("../config.mk", "TestCharm.cpp", "MakefileTmp")
    buildMakefile(config, file, makefileName)
    os.system("make -f %s" % makefileName)
    
    
