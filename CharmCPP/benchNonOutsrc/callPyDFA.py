from charm.toolbox.DFA import *
import sys

def strTuple(j):
    s = ""
    for i in j: 
        s += str(i) + ","
    s = s[:-1]
    return s

def strList(_list):
    s = ""
    for i in _list:
        if type(i) == tuple: i = str(strTuple(i))
        s += str(i) + ":"
    s = s[:-1]
    return s

def strDict(_dict):
    s = ""
    for i,j in _dict.items():
        if type(j) == tuple: j = str(strTuple(j))
        s += str(j) + ":"
    s = s[:-1]
    return s

def constructDFA(k, alpha, file):
    alphabet = set(str(alpha))
    dfa = DFA(k, alphabet)
    M = dfa.constructDFA()
    Q, S, T, q0, F = M
    f = open(file, 'w')
    f.write("Q=%s\n" % strList(Q))
    f.write("T=%s\n" % strList(T))
    f.write("q0=%s\n" % q0)
    f.write("F=%s\n" % strList(F))
    f.close()
    return 

def getTransitions(k, alpha, file, w):
    alphabet = set(str(alpha))
    dfa = DFA(k, alphabet)
    M = dfa.constructDFA()
    Ti = dfa.getTransitions(M, w)
    f = open(file, 'w')
    f.write("Ti=%s\n" % strDict(Ti))
    f.close()
    return

def isStrAccept(k, alpha, file, w):
    alphabet = set(str(alpha))
    dfa = DFA(k, alphabet)
    M = dfa.constructDFA()
    res = dfa.accept(M, w)
    if res: i = 1
    else: i = 0
    f = open(file, 'w')
    f.write("accept=%s\n" % i)
    f.close()
    return


def getAcceptState(k, alpha, file, TiStr):
    alphabet = set(str(alpha))
    dfa = DFA(k, alphabet)
    M = dfa.constructDFA()
    Ti = eval(TiStr)
    x = dfa.getAcceptState(Ti)
    f = open(file, 'w')
    f.write("x=%s\n" % x)
    f.close()
    return
    


if __name__ == "__main__":
   #print(sys.argv[1:])
   cmd = sys.argv[1]
   if cmd == "-c":
      constructDFA(sys.argv[2], sys.argv[3], sys.argv[4])
   elif cmd == "-t":
      getTransitions(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
   elif cmd == "-ga":
      getAcceptState(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]) 
   elif cmd == "-a":
      isStrAccept(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
