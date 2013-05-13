""" Module re_compile -- compile a regular expression into an FSA

To Do
-----
New features:
    - add \-, \~
    - add remaining metachars
    - char set with ^ as first char will print wrong
    - figure out when to print spaces between operators
"""

__author__  = "Oliver Steele <steele@osteele.com>"

from functools import reduce
import charm.toolbox.FSA as FSA

def compileSymbolRE(str):
    return SymbolRECompiler(str).toFSA()

def dummy_func(a, b):
    return a, b 
    
class SymbolRECompiler:
    EOF = -1
    
    def __init__(self, str, recordSourcePositions=0):
        self.str = str
        self.recordSourcePositions = recordSourcePositions
    
    def toFSA(self, minimize=1):
        self.index = 0
        self.nextToken = None
        fsa = self.compileExpr()
        if self.index < len(self.str):
            raise ValueError('extra ' + str(')'))
        del self.index
        fsa.label = self.str
        if minimize:
            fsa = fsa.minimized()
        return fsa
    
    def readChar(self):
        if self.index < len(self.str):
            c, self.index = self.str[self.index], self.index + 1
            return c
    
    def peekChar(self):
        if self.index < len(self.str):
            return self.str[self.index]
    
    def readToken(self):
        token = self.nextToken or self._readNextToken()
        self.nextToken = None
        return token != self.EOF and token
    
    def peekToken(self):
        token = self.nextToken = self.nextToken or self._readNextToken()
        #print 'peekToken', token
        return token != self.EOF and token
    
    def _readNextToken(self):
        c = self.readChar()
        if not c:
            return self.EOF
        elif c in '()|&':
            return c
        elif c == '.':
            return ANY
        return c
    
    def skipTokens(self, bag):
        while self.peekToken() and self.peekToken() in bag:
            self.readToken()
    
    def compileExpr(self):
        fsa = FSA.NULL_FSA
        while self.peekToken() and self.peekToken() != ')':
            fsa = FSA.union(fsa, self.compileConjunction())
            self.skipTokens(['|'])
        return fsa
    
    def compileConjunction(self):
        fsa = None
        while self.peekToken() and self.peekToken() not in (')', '|'):
            sequence = self.compileSequence()
            fsa = fsa and FSA.intersection(fsa, sequence) or sequence
            self.skipTokens(['&'])
        return fsa
    
    def compileSequence(self):
        fsa = FSA.EMPTY_STRING_FSA
        while self.peekToken() and self.peekToken() not in (')', '|', '&'):
            fsa = FSA.concatenation(fsa, self.compileItem())
        return fsa
    
    def compileItem(self):
        startPosition = self.index
        c = self.readToken()
        if c == '(':
            fsa = self.compileExpr()
            if self.readToken() != ')':
                raise ValueError("missing ')'")
        elif c == '~':
            fsa = FSA.complement(self.compileItem())
        else:
            fsa = FSA.singleton(c, arcMetadata=self.recordSourcePositions and [startPosition])
        while self.peekChar() and self.peekChar() in '?*+':
            c = self.readChar()
            if c == '*':
                fsa = FSA.closure(fsa)
            elif c == '?':
                fsa = FSA.union(fsa, FSA.EMPTY_STRING_FSA)
            elif c == '+':
                fsa = FSA.iteration(fsa)
            else:
                raise ValueError('program error')
        return fsa


#
# Character REs
#

class CharacterSet:
    def __init__(self, ranges):
        if type(ranges) == str:
            ranges = self.convertString(ranges)
        accum = []
        # copy, so sort doesn't destroy the arg
        for item in ranges:
            if type(item) == tuple:
                if len(item) == 1:
                    accum.append((item, item))
                elif len(item) == 2:
                    accum.append(item)
                else:
                    raise ValueError("invalid argument to CharacterSet")
            elif type(item) == str:
                for c in item:
                    accum.append((c, c))
            else:
                raise ValueError("invalid argument to CharacterSet")
        ranges = accum
        ranges.sort()
        index = 0
        while index < len(ranges) - 1:
            [(c0, c1), (c2, c3)] = ranges[index:index + 2]
            if c1 >= c2:
                ranges[index:index + 2] = [(c0, max(c1, c3))]
            else:
                index = index + 1
        self.ranges = ranges
    
    def __cmp__(self, other):
        return cmp(type(self), type(other)) or cmp(self.__class__, other.__class__) or cmp(self.ranges, other.ranges)

    def __hash__(self):
        return reduce(lambda a, b:a ^ b, map(hash, self.ranges))
    
    def convertString(self, _str):
        ranges = []
        index = 0
        while index < len(_str):
            c0 = c1 = _str[index]
            index = index + 1
            if index + 1 < len(_str) and _str[index ] == '-':
                c1 = _str[index + 1]
                index = index + 2
            ranges.append((c0, c1))
        return ranges
    
    def matches(self, c):
        for c0, c1 in self.ranges:
            if c0 <= c and c <= c1:
                return 1
        return 0
    
    def complement(self):
        results = []
        for (_, c0), (c1, _) in map(dummy_func, [(None, None)] + self.ranges, self.ranges + [(None, None)]):
            i0 = c0 and ord(c0) + 1 or 0
            i1 = c1 and ord(c1) - 1 or 255
            if i0 <= i1:
                results.append((chr(i0), chr(i1)))
        if results:
            return CharacterSet(results)
    
    def union(self, other):
        a = self.complement()
        b = other.complement()
        if a and b:
            c = a.intersection(b)
            if c:
                return c.complement()
            else:
                return self.ANY
        else:
            return a or b

    def __add__(self, other):
        return self.union(other)
    
    def intersection(self, other):
        if self.ranges == other.ranges:
            return self
        results = []
        for (a0, a1) in self.ranges:
            for (b0, b1) in other.ranges:
                c0 = max(a0, b0)
                c1 = min(a1, b1)
                if c0 <= c1:
                    results.append((c0, c1))
        results.sort()
        if results:
            return CharacterSet(results)
    
    def __str__(self):
        """
        ### print(CharacterSet([('a', 'a')]))
        a
        ### print(CharacterSet([('a', 'b')]))
        [ab]
        """
        if self == self.ANY:
            return '.'
        elif not self.ranges:
            return '[^.]'
        for key, value in METACHARS.items():
            if self == value:
                return '\\' + key
        ranges = self.ranges
        if len(ranges) == 1 and ranges[0][0] == ranges[0][1]:
            return ranges[0][0]
        if ranges[0][0] == chr(0) and ranges[-1][1] == chr(255):
            s = str(self.complement())
            if s[0] == '[' and s[-1] == ']':
                s = s[1:-1]
            return '[^' + s + ']'
        s = ''
        for c0, c1 in ranges:
            if c0 == c1 and c0 != '-':
                s = s + self.crep(c0)
            elif ord(c0) + 1 == ord(c1) and c0 != '-' and c1 != '-':
                s = s + "%s%s" % (self.crep(c0), self.crep(c1))
            else:
                s = s + "%s-%s" % (self.crep(c0), self.crep(c1))
        return '[' + s + ']'
    
    def crep(self, c):
        return {'\t': '\\t', '\n': '\\n', '\r': '\\r', '\f': '\\f', '\v': '\\v'}.get(c, c)
    
    def __repr__(self):
        return '<' + self.__class__.__name__ + ' ' + str(self) + '>'

METACHARS = {
        'd': CharacterSet('0-9'),
        's': CharacterSet(' \t\n\r\f\v'),
        'w': CharacterSet('a-zA-Z0-9')}
METACHARS['D'] = METACHARS['d'].complement()
METACHARS['S'] = METACHARS['s'].complement()
METACHARS['W'] = METACHARS['w'].complement()

CharacterSet.ANY = CharacterSet([(chr(0), chr(255))])


class RECompiler(SymbolRECompiler):
    def _readNextToken(self):
        c = self.readChar()
        if not c:
            return self.EOF
        elif c in '()|':
            return c
        elif c == '.':
            return CharacterSet.ANY
        elif c == '[':
            if self.peekChar() == '~':
                self.readChar()
                return self.readCSetInnards().complement()
            else:
                return self.readCSetInnards()
        elif c == '\\':
            c = self.readChar()
            if METACHARS.get(c):
                return METACHARS.get(c)
            elif c == '&':
                return c
            else:
                return CharacterSet([(c,c)])
        else:
            return CharacterSet([(c,c)])
    
    def readCSetInnards(self):
        cset = CharacterSet([])
        while 1:
            c = self.readChar()
            if c == ']':
                return cset
            if self.peekChar() == '-':
                self.readChar()
                cset = cset.union(CharacterSet([(c, self.readChar())]))
            else:
                cset = cset.union(CharacterSet([(c, c)]))

def compileRE(_str, minimize=1, recordSourcePositions=0):
    return RECompiler(_str, recordSourcePositions=recordSourcePositions).toFSA(minimize=minimize)

#
# testing
#
def _printCompiledREs():
    print (compileRE('a'))
    print (compileRE('ab'))
    print (compileRE('a|b'))
    print (compileRE('abc'))
    print (compileRE('ab*c'))
    print (compileRE('ab?c'))
    print (compileRE('ab+c'))
    print (compileRE('ab|c'))
    print (compileRE('a(b|c)'))
    #print compileRE('a\&a')
    #print compileRE('ab+\&a+b')
    #print compileRE('ab*\&a*b')
    print (compileRE('ab|c?'))
    print (compileRE('ab|bc?'))
    print (compileRE('a?'))
    print (compileRE('abc|acb|bac|bca|cab|cba'))
    print (compileRE('abc|acb|bac|bca|cab|cba', 0).determinized())
    print (compileRE('abc|acb|bac|bca|cab|cba', 0).determinized())
    print (compileRE('abc|acb|bac|bca|cab|cba', 0).minimized())
    print (compileRE('abc|acb|bac|bca|cab', 0).determinized())

    print (compileRE('a', 0))
    print (compileRE('a', 0).determinized())
    print (compileRE('ab', 0).determinized())
    print (compileRE('a', 0).minimized())
    print (compileRE('ab', 0).minimized())
    print (compileRE('a'))
    print (compileRE('a|b', 0).determinized())
    print (compileRE('a|b', 0).minimized().getArcMetadata())
    print (compileRE('a|b', 0).minimized())

def _test(reset=0):
    import doctest, compileRE
    if reset:
        doctest.master = None # This keeps doctest from complaining after a reload.
    return doctest.testmod(compileRE)
