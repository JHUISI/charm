from charm.toolbox.reCompiler import *
from charm.toolbox.FSA import FSA


class DFA:
    def __init__(self, regex, alphabet):
        assert type(regex) == str, "'regex' needs to be a string"
        self.fsa = compileRE(regex)
        self.alphabet = alphabet
    
    # a sample DFA...
    #Q = [0, 1, 2]
    #T = [ (0, 1, 'a'), (1, 1, 'b'), (1, 2, 'a') ]
    #q0 = 0
    #F = [2]
    #dfaM = [Q, T, q0, F]
    def constructDFA(self):
        # self.states, self.alphabet, self.transitions, self.initialState, self.finalStates
        Q, alphabet, T, q0, F = self.fsa.tuple()
        newT = []
        for t in T:
            # convert the CharSet to a Python string
            (x, y, s) = t 
            newT.append( (x, y, str(s)) )
        Q.sort()
        alphabet = list(self.alphabet)
        return [Q, alphabet, newT, q0, F]
    
    def accept(self, M, s):
        Q, S, T, q0, F = M
        fsa1 = FSA(Q, S, T, q0, F)
        s_str = ""
        if type(s) == str:
            return fsa1.accepts(s)
        elif type(s) == dict:
            keys = list(s.keys())
            keys.sort()
            for i in keys:
                s_str += str(s[i])
            return fsa1.accepts(s_str)
        elif type(s) in [list, tuple, set]:
            for i in s:
                s_str += str(i)
            return fsa1.accepts(s_str)
        else:
            raise ValueError("unexpected type!")
    
    def getTransitions(self, M, s):
        Q, S, T, q0, F = M
        fsa1 = FSA(Q, S, T, q0, F)
        s_str = ""
        if type(s) == str:
            return fsa1.getTransitions(s)
        elif type(s) == dict:
            keys = list(s.keys())
            keys.sort()
            for i in keys:
                s_str += str(s[i])
            return fsa1.getTransitions(s_str)
        elif type(s) in [list, tuple, set]:
            for i in s:
                s_str += str(i)
            return fsa1.getTransitions(s_str)
        else:
            raise ValueError("unexpected type!")
        
    def getAcceptState(self, transitions):
        assert type(transitions) == dict, "'transitions' not the right type"
        t_len = len(transitions.keys())
        return int(transitions[t_len][1])
        
    def getSymbols(self, s):
        assert type(s) == str
        result = {}
        count = 1 # 1-indexed
        for i in s:
            result[ count ] = i
            count += 1
        return result

if __name__ == "__main__":    
    alphabet = {'a', 'b'}
    dfa = DFA("ab*a", alphabet)
    dfaM = dfa.constructDFA()
    
    print("Accept? %s" % dfa.accept(dfaM, "abba"))
    print("Accept? %s" % dfa.accept(dfaM, "aba"))
    print("Accept? %s" % dfa.accept(dfaM, "abc"))
    
