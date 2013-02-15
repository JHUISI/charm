from __future__ import print_function
import logging

logger = None
print2screen = False

def setup(appName, pathToTmp, logLevel=logging.INFO):
    logger = logging.getLogger(appName)
    hdlr = logging.FileHandler(pathToTmp)
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logLevel)
    return logger
    
def info(*args):
    outputStr = ""
    for i in args:
        outputStr += str(i)
    
    #assert logger != None, "logger not set. Call setup first."
    if logger == None or print2screen:
        print(*args)

    logger.info(outputStr)
    return

def error(*args):
    outputStr = ""
    for i in args:
        outputStr += str(i)
    
    #assert logger != None, "logger not set. Call setup first."
    if logger == None or print2screen:
        print(*args)

    logger.info(outputStr)
    return
