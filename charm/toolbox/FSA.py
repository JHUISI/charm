
# Module FSA -- methods to manipulate finite-state automata

"""
This module defines an FSA class, for representing and operating on
finite-state automata (FSAs). FSAs can be used to represent regular
expressions and to test sequences for membership in the languages
described by regular expressions.

FSAs can be deterministic or nondeterministic, and they can contain
epsilon transitions. Methods to determinize an automaton (also
eliminating its epsilon transitions), and to minimize an automaton,
are provided.

The transition labels for an FSA can be symbols from an alphabet, as
in the standard formal definition of an FSA, but they can also be
instances which represent predicates. If these instances implement
instance.matches(), then the FSA nextState() function and accepts()
predicate can be used. If they implement instance.complement() and
instance.intersection(), the FSA can be be determinized and minimized,
to find a minimal deterministic FSA that accepts an equivalent
language.


Quick Start
----------
Instances of FSA can be created out of labels (for instance, strings)
by the singleton() function, and combined to create more complex FSAs
through the complement(), closure(), concatenation(), union(), and
other constructors. For example, concatenation(singleton('a'),
union(singleton('b'), closure(singleton('c')))) creates an FSA that
accepts the strings 'a', 'ab', 'ac', 'acc', 'accc', and so on.

Instances of FSA can also be created with the compileRE() function,
which compiles a simple regular expression (using only '*', '?', '+',
'|', '(', and ')' as metacharacters) into an FSA. For example,
compileRE('a(b|c*)') returns an FSA equivalent to the example in the
previous paragraph.

FSAs can be determinized, to create equivalent FSAs (FSAs accepting
the same language) with unique successor states for each input, and
minimized, to create an equivalent deterministic FSA with the smallest
number of states. FSAs can also be complemented, intersected, unioned,
and so forth as described under 'FSA Functions' below.


FSA Methods
-----------
The class FSA defines the following methods.

Acceptance
``````````
fsa.nextStates(state, input)
  returns a list of states
fsa.nextState(state, input)
  returns None or a single state if
  |nextStates| <= 1, otherwise it raises an exception
fsa.nextStateSet(states, input)
  returns a list of states
fsa.accepts(sequence)
  returns true or false

Accessors and predicates
````````````````````````
isEmpty()
  returns true iff the language accepted by the FSA is the empty language
labels()
  returns a list of labels that are used in any transition
nextAvailableState()
  returns an integer n such that no states in the FSA
  are numeric values >= n

Reductions
``````````
sorted(initial=0)
  returns an equivalent FSA whose states are numbered
  upwards from 0
determinized()
  returns an equivalent deterministic FSA
minimized()
  returns an equivalent minimal FSA
trimmed()
  returns an equivalent FSA that contains no unreachable or dead
  states

Presentation
````````````
toDotString()
  returns a string suitable as *.dot file for the 'dot'
  program from AT&T GraphViz
view()
  views the FSA with a gs viewer, if gs and dot are installed


FSA Functions
------------
Construction from FSAs
``````````````````````
complement(a)
  returns an fsa that accepts exactly those sequences that its
  argument does not
closure(a)
  returns an fsa that accepts sequences composed of zero or more
  concatenations of sequences accepted by the argument
concatenation(a, b)
  returns an fsa that accepts sequences composed of a
  sequence accepted by a, followed by a sequence accepted by b
containment(a, occurrences=1)
  returns an fsa that accepts sequences that
  contain at least occurrences occurrences of a subsequence recognized by the
  argument.
difference(a, b)
  returns an fsa that accepts those sequences accepted by a
  but not b
intersection(a, b)
  returns an fsa that accepts sequences accepted by both a
  and b
iteration(a, min=1, max=None)
  returns an fsa that accepts sequences
  consisting of from min to max (or any number, if max is None) of sequences
  accepted by its first argument
option(a)
  equivalent to union(a, EMPTY_STRING_FSA)
reverse(a)
  returns an fsa that accepts strings whose reversal is accepted by
  the argument
union(a, b)
  returns an fsa that accepts sequences accepted by both a and b

Predicates
``````````
equivalent(a, b)
  returns true iff a and b accept the same language

Reductions (these equivalent to the similarly-named methods)
````````````````````````````````````````````````````````````
determinize(fsa)
  returns an equivalent deterministic FSA
minimize(fsa)
  returns an equivalent minimal FSA
sort(fsa, initial=0)
  returns an equivalent FSA whose states are numbered from
  initial
trim(fsa)
  returns an equivalent FSA that contains no dead or unreachable
  states

Construction from labels
````````````````````````
compileRE(string)
  returns an FSA that accepts the language described by
  string, where string is a list of symbols and '*', '+', '?', and '|' operators,
    with '(' and ')' to control precedence.
sequence(sequence)
  returns an fsa that accepts sequences that are matched by
  the elements of the argument. For example, sequence('abc') returns an fsa that
  accepts 'abc' and ['a', 'b', 'c'].
singleton(label)
  returns an fsa that accepts singletons whose elements are
  matched by label. For example, singleton('a') returns an fsa that accepts only
  the string 'a'.


FSA Constants
------------
EMPTY_STRING_FSA is an FSA that accepts the language consisting only
of the empty string.

NULL_FSA is an FSA that accepts the null language.

UNIVERSAL_FSA is an FSA that accepts S*, where S is any object.


FSA instance creation
---------------------
FSA is initialized with a list of states, an alphabet, a list of
transition, an initial state, and a list of final states. If fsa is an
FSA, fsa.tuple() returns these values in that order, i.e. (states,
alphabet, transitions, initialState, finalStates). They're also
available as fields of fsa with those names.

Each element of transition is a tuple of a start state, an end state,
and a label: (startState, endSTate, label).

If the list of states is None, it's computed from initialState,
finalStates, and the states in transitions.

If alphabet is None, an open alphabet is used: labels are assumed to
be objects that implements label.matches(input), label.complement(),
and label.intersection() as follows:

    - label.matches(input) returns true iff label matches input
    - label.complement() returnseither a label or a list of labels which,
        together with the receiver, partition the input alphabet
    - label.intersection(other) returns either None (if label and other don't
        both match any symbol), or a label that matches the set of symbols that
        both label and other match

As a special case, strings can be used as labels. If a strings 'a' and
'b' are used as a label and there's no alphabet, '~a' and '~b' are
their respective complements, and '~a&~b' is the intersection of '~a'
and '~b'. (The intersections of 'a' and 'b', 'a' and '~b', and '~a'
and 'b' are, respectively, None, 'a', and 'b'.)


Goals
-----
Design Goals:

- easy to use
- easy to read (simple implementation, direct expression of algorithms)
- extensible

Non-Goals:

- efficiency
"""

__author__  = "Oliver Steele <steele@osteele.com>"

# Python 3 port of the FSA module 
from functools import reduce

#try:
#    import NumFSAUtils
#except ImportError:
NumFSAUtils = None

ANY = 'ANY'
EPSILON = None

TRACE_LABEL_MULTIPLICATIONS = 0
NUMPY_DETERMINIZATION_CUTOFF = 50

class FSA:
    def __init__(self, states, alphabet, transitions, initialState, finalStates, arcMetadata=[]):
        if states == None:
            states = self.collectStates(transitions, initialState, finalStates)
        else:
            #assert not filter(lambda s, states=states:s not in states, self.collectStates(transitions, initialState, finalStates))
            assert list(filter(lambda s, states=states:s not in states, self.collectStates(transitions, initialState, finalStates))) != None
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initialState = initialState
        self.finalStates = finalStates
        self.setArcMetadata(arcMetadata)
    
    
    #
    # Initialization
    #
    def makeStateTable(self, default=None):
        for state in self.states:
            if type(state) != int:
                return {}
        if reduce(min, self.states) < 0: return {}
        if reduce(max, self.states) > max(100, len(self.states) * 2): return {}
        return [default] * (reduce(max, self.states) + 1)
    
    def initializeTransitionTables(self):
        self._transitionsFrom = self.makeStateTable()
        for s in self.states:
            self._transitionsFrom[s] = []
        for transition in self.transitions:
            s, _, label = transition
            self._transitionsFrom[s].append(transition)
    
    def collectStates(self, transitions, initialState, finalStates):
        states = finalStates[:]
        if initialState not in states:
            states.append(initialState)
        for s0, s1, _ in transitions:
            if s0 not in states: states.append(s0)
            if s1 not in states: states.append(s1)
        states.sort()
        return states
    
    def computeEpsilonClosure(self, state):
        states = [state]
        index = 0
        while index < len(states):
            state, index = states[index], index + 1
            for _, s, label in self.transitionsFrom(state):
                if label == EPSILON and s not in states:
                    states.append(s)
        states.sort()
        return states
    
    def computeEpsilonClosures(self):
        self._epsilonClosures = self.makeStateTable()
        for s in self.states:
            self._epsilonClosures[s] = self.computeEpsilonClosure(s)
    
    
    #
    # Copying
    #
    def create(self, *args):
        return self.__class__(*args)
    
    def copy(self, *args):
        copy = self.__class__(*args)
        if hasattr(self, 'label'):
            copy.label = self.label
        if hasattr(self, 'source'):
            copy.source = self.source
        return copy
    
    def creationArgs(self):
        return self.tuple() + (self.getArcMetadata(),)
    
    def coerce(self, klass):
        copy = klass(*self.creationArgs())
        if hasattr(self, 'source'):
            copy.source = self.source
        return copy
    
    
    #
    # Accessors
    #
    def epsilonClosure(self, state):
        try:
            return self._epsilonClosures[state]
        except AttributeError:
            self.computeEpsilonClosures()
        return self._epsilonClosures[state]
    
    def labels(self):
        """Returns a list of transition labels."""
        labels = []
        for (_, _, label) in self.transitions:
            if label and label not in labels:
                labels.append(label)
        return labels
    
    def nextAvailableState(self):
        return reduce(max, [s for s in self.states if type(s) == int], -1) + 1
    
    def transitionsFrom(self, state):
        try:
            return self._transitionsFrom[state]
        except AttributeError:
            self.initializeTransitionTables()
        return self._transitionsFrom[state]
    
    def tuple(self):
        return self.states, self.alphabet, self.transitions, self.initialState, self.finalStates
    
    
    #
    # Arc Metadata Accessors
    #
    def hasArcMetadata(self):
        return hasattr(self, '_arcMetadata')
    
    def getArcMetadata(self):
        return list(getattr(self, '_arcMetadata', {}).items())
    
    def setArcMetadata(self, list):
        arcMetadata = {}
        for (arc, data) in list:
            arcMetadata[arc] = data
        self._arcMetadata = arcMetadata
    
    def addArcMetadata(self, list):
        for (arc, data) in list:
            self.addArcMetadataFor(arc, data)
    
    def addArcMetadataFor(self, transition, data):
        if not hasattr(self, '_arcMetadata'):
            self._arcMetadata = {}
        oldData = self._arcMetadata.get(transition)
        if oldData:
            for item in data:
                if item not in oldData:
                    oldData.append(item)
        else:
            self._arcMetadata[transition] = data
        
    def setArcMetadataFor(self, transition, data):
        if not hasattr(self, '_arcMetadata'):
            self._arcMetadata = {}
        self._arcMetadata[transition] = data
    
    def getArcMetadataFor(self, transition, default=None):
        return getattr(self, '_arcMetadata', {}).get(transition, default)
    
    
    #
    # Predicates
    #
    def isEmpty(self):
        return not self.minimized().finalStates
    
    def isFSA(self):
        return 1
    
    
    #
    # Accepting
    #
    def labelMatches(self, label, input):
        return labelMatches(label, input)
    
    def nextStates(self, state, input):
        states = []
        for _, sink, label in self.transitionsFrom(state):
            if self.labelMatches(label, input) and sink not in states:
                states.extend(self.epsilonClosure(sink))
        return states
    
    def nextState(self, state, input):
        states = self.nextStates(state, input)
        assert len(states) <= 1
        return states and states[0]
    
    def nextStateSet(self, states, input):
        successors = []
        for state in states:
            for _, sink, label in self.transitionsFrom(state):
                if self.labelMatches(label, input) and sink not in successors:
                    successors.append(sink)
        return successors
    
    def accepts(self, sequence):
        states = [self.initialState]
        for item in sequence:
            newStates = []
            for state in states:
                for s1 in self.nextStates(state, item):
                    if s1 not in newStates:
                        newStates.append(s1)
            states = newStates
        return len(list(filter(lambda s, finals=self.finalStates:s in finals, states))) > 0
    
    def getTransitions(self, sequence):
        states = [self.initialState]
        transitions = {}
        count = 1
        for item in sequence:
            newStates = []
            for state in states:
                for s1 in self.nextStates(state, item):
                    if s1 not in newStates:
                        transitions[ count ] = (int(state), int(s1), str(item))
                        count += 1
#                        print("s1: " % (state, s1, str(item)))
                        newStates.append(s1)
            states = newStates
        if len(list(filter(lambda s, finals=self.finalStates:s in finals, states))) > 0:
            return transitions
        return False
    
    #
    # FSA operations
    #
    def complement(self):
        states, alpha, transitions, start, finals = completion(self.determinized()).tuple()
        return self.create(states, alpha, transitions, start, list(filter(lambda s,f=finals:s not in f, states)))#.trimmed()
    
    
    #
    # Reductions
    #
    def sorted(self, initial=0):
        if hasattr(self, '_isSorted'):
            return self
        stateMap = {}
        nextState = initial
        states, index = [self.initialState], 0
        while index < len(states) or len(states) < len(self.states):
            if index >= len(states):
                for state in self.states:
                    if stateMap.get(state) == None:
                        break
                states.append(state)
            state, index = states[index], index + 1
            new, nextState = nextState, nextState + 1
            stateMap[state] = new
            for _, s, _ in self.transitionsFrom(state):
                if s not in states:
                    states.append(s)
        states = list(stateMap.values())
        transitions = list(map(lambda s, m=stateMap:(m[s[0]], m[s[1]], s[2]), self.transitions))
        arcMetadata = list(map(lambda s, data, m=stateMap:((m[s[0]], m[s[1]], s[2]), data), self.getArcMetadata()))
        copy = self.copy(states, self.alphabet, transitions, stateMap[self.initialState], list(map(stateMap.get, self.finalStates)), arcMetadata)
        copy._isSorted = 1
        return copy
    
    def trimmed(self):
        """Returns an equivalent FSA that doesn't include unreachable states,
        or states that only lead to dead states."""
        if hasattr(self, '_isTrimmed'):
            return self
        states, alpha, transitions, initial, finals = self.tuple()
        reachable, index = [initial], 0
        while index < len(reachable):
            state, index = reachable[index], index + 1
            for (_, s, _) in self.transitionsFrom(state):
                if s not in reachable:
                    reachable.append(s)
        endable, index = list(finals), 0
        while index < len(endable):
            state, index = endable[index], index + 1
            for (s0, s1, _) in transitions:
                if s1 == state and s0 not in endable:
                    endable.append(s0)
        states = []
        for s in reachable:
            if s in endable:
                states.append(s)
        if not states:
            if self.__class__  == FSA:
                return NULL_FSA
            else:
                return NULL_FSA.coerce(self.__class__)
        transitions = list(filter(lambda s, states=states: s[0] in states and s[1] in states, transitions))
        arcMetadata = list(filter(lambda s, states=states: s[0] in states and s[1] in states, self.getArcMetadata()))
        result = self.copy(states, alpha, transitions, initial, list(filter(lambda s, states=states:s in states, finals)), arcMetadata).sorted()
        result._isTrimmed = 1
        return result
    
    def withoutEpsilons(self):
        # replace each state by its epsilon closure
        states0, alphabet, transitions0, initial0, finals0 = self.tuple()
        initial = self.epsilonClosure(self.initialState)
        initial.sort()
        initial = tuple(initial)
        stateSets, index = [initial], 0
        transitions = []
        while index < len(stateSets):
            stateSet, index = stateSets[index], index + 1
            for (s0, s1, label) in transitions0:
                if s0 in stateSet and label:
                    target = self.epsilonClosure(s1)
                    target.sort()
                    target = tuple(target)
                    transition = (stateSet, target, label)
                    if transition not in transitions:
                        transitions.append(transition)
                    if target not in stateSets:
                        stateSets.append(target)
        finalStates = []
        for stateSet in stateSets:
            if list(filter(lambda s, finalStates=self.finalStates:s in finalStates, stateSet)):
                finalStates.append(stateSet)
        copy = self.copy(stateSets, alphabet, transitions, stateSets[0], finalStates).sorted()
        copy._isTrimmed = 1
        return copy
    
    def determinized(self):
        """Returns a deterministic FSA that accepts the same language."""
        if hasattr(self, '_isDeterminized'):
            return self
        if len(self.states) > NUMPY_DETERMINIZATION_CUTOFF and NumFSAUtils and not self.getArcMetadata():
            data = NumFSAUtils.determinize(*self.tuple() + (self.epsilonClosure,))
            result = apply(self.copy, data).sorted()
            result._isDeterminized = 1
            return result
        transitions = []
        stateSets, index = [tuple(self.epsilonClosure(self.initialState))], 0
        arcMetadata = []
        while index < len(stateSets):
            stateSet, index = stateSets[index], index + 1
            localTransitions = list(filter(lambda s, set=stateSet:s[2] and s[0] in set, self.transitions))
            if localTransitions:
                localLabels = list(map(lambda s:s[2], localTransitions))
                labelMap = constructLabelMap(localLabels, self.alphabet)
                labelTargets = {}   # a map from labels to target states
                for transition in localTransitions:
                    _, s1, l1 = transition
                    for label, positives in labelMap:
                        if l1 in positives:
                            successorStates = labelTargets[label] = labelTargets.get(label) or []
                            for s2 in self.epsilonClosure(s1):
                                if s2 not in successorStates:
                                    successorStates.append(s2)
                            if self.getArcMetadataFor(transition):
                                arcMetadata.append(((stateSet, successorStates, label), self.getArcMetadataFor(transition)))
                for label, successorStates in list(labelTargets.items()):
                    successorStates.sort()
                    successorStates = tuple(successorStates)
                    transitions.append((stateSet, successorStates, label))
                    if successorStates not in stateSets:
                        stateSets.append(successorStates)
        finalStates = []
        for stateSet in stateSets:
            if list(filter(lambda s,finalStates=self.finalStates:s in finalStates, stateSet)):
                finalStates.append(stateSet)
        if arcMetadata:
            def fixArc(pair):
                (s0, s1, label), data = pair
                s1.sort()
                s1 = tuple(s1)
                return ((s0, s1, label), data)
            arcMetadata = list(map(fixArc, arcMetadata))
        result = self.copy(stateSets, self.alphabet, transitions, stateSets[0], finalStates, arcMetadata).sorted()
        result._isDeterminized = 1
        result._isTrimmed = 1
        return result
    
    def minimized(self):
        """Returns a minimal FSA that accepts the same language."""
        if hasattr(self, '_isMinimized'):
            return self
        self = self.trimmed().determinized()
        states0, alpha0, transitions0, initial0, finals0 = self.tuple()
        sinkState = self.nextAvailableState()
        labels = self.labels()
        states = [_f for _f in [
                tuple(filter(lambda s, finalStates=self.finalStates:s not in finalStates, states0)),
                tuple(filter(lambda s, finalStates=self.finalStates:s in finalStates, states0))] if _f]
        labelMap = {}
        for state in states0:
            for label in labels:
                found = 0
                for s0, s1, l in self.transitionsFrom(state):
                    if l == label:
                        assert not found
                        found = 1
                        labelMap[(state, label)] = s1
        changed = 1
        iteration = 0
        while changed:
            changed = 0
            iteration = iteration + 1
            #print 'iteration', iteration
            partitionMap = {sinkState: sinkState}
            for set in states:
                for state in set:
                    partitionMap[state] = set
            #print 'states =', states
            for index in range(len(states)):
                set = states[index]
                if len(set) > 1:
                    for label in labels:
                        destinationMap = {}
                        for state in set:
                            nextSet = partitionMap[labelMap.get((state, label), sinkState)]
                            targets = destinationMap[nextSet] = destinationMap.get(nextSet) or []
                            targets.append(state)
                        #print 'destinationMap from', set, label, ' =', destinationMap
                        if len(list(destinationMap.values())) > 1:
                            values = list(destinationMap.values())
                            #print 'splitting', destinationMap.keys()
                            for value in values:
                                value.sort()
                            states[index:index+1] = list(map(tuple, values))
                            changed = 1
                            break
        transitions = removeDuplicates(list(map(lambda s, m=partitionMap:(m[s[0]], m[s[1]], s[2]), transitions0)))
        arcMetadata = list(map(lambda s, data, m=partitionMap:((m[s[0]], m[s[1]], s[2]), data), self.getArcMetadata()))
        if not alpha0:
            newTransitions = consolidateTransitions(transitions)
            if arcMetadata:
                newArcMetadata = []
                for transition, data in arcMetadata:
                    s0, s1, label = transition
                    for newTransition in newTransitions:
                        if newTransition[0] == s0 and newTransition[1] == s1 and labelIntersection(newTransition[2], label):
                            newArcMetadata.append((newTransition, data))
                arcMetadata = newArcMetadata
            transitions = newTransitions
        initial = partitionMap[initial0]
        finals = removeDuplicates(list(map(lambda s, m=partitionMap:m[s], finals0)))
        result = self.copy(states, self.alphabet, transitions, initial, finals, arcMetadata).sorted()
        result._isDeterminized = 1
        result._isMinimized = 1
        result._isTrimmed = 1
        return result
    
    
    #
    # Presentation Methods
    #
    def __repr__(self):
        if hasattr(self, 'label') and self.label:
            return '<%s on %s>' % (self.__class__.__name__, self.label)
        else:
            return '<%s.%s instance>' % (self.__class__.__module__, self.__class__.__name__)
    
    def __str__(self):
        import string
        output = []
        output.append('%s {' % (self.__class__.__name__,))
        output.append('\tinitialState = ' + str(self.initialState) + ';')
        if self.finalStates:
            output.append('\tfinalStates = ' + string.join(list(map(str, self.finalStates)), ', ') + ';')
        transitions = list(self.transitions)
        transitions.sort()
        for transition in transitions:
            (s0, s1, label) = transition
            additionalInfo = self.additionalTransitionInfoString(transition)
            output.append('\t%s -> %s %s%s;' % (s0, s1, labelString(label), additionalInfo and ' ' + additionalInfo or ''));
        output.append('}');
        return string.join(output, '\n')
    
    def additionalTransitionInfoString(self, transition):
        if self.getArcMetadataFor(transition):
            import string
            return '<' + string.join(list(map(str, self.getArcMetadataFor(transition))), ', ') + '>'
    
    def stateLabelString(self, state):
        """A template method for specifying a state's label, for use in dot
        diagrams. If this returns None, the default (the string representation
        of the state) is used."""
        return None
    
    def toDotString(self):
        """Returns a string that can be printed by the DOT tool at
        http://www.research.att.com/sw/tools/graphviz/ ."""
        import string
        output = []
        output.append('digraph finite_state_machine {');
        if self.finalStates:
                output.append('\tnode [shape = doublecircle]; ' + string.join(list(map(str, self.finalStates)), '; ') + ';' );
        output.append('\tnode [shape = circle];');
        output.append('\trankdir=LR;');
        output.append('\t%s [style = bold];' % (self.initialState,))
        for state in self.states:
            if self.stateLabelString(state):
                output.append('\t%s [label = "%s"];' % (state, string.replace(self.stateLabelString(state), '\n', '\\n')))
        transitions = list(self.transitions)
        transitions.sort()
        for (s0, s1, label) in transitions:
            output.append('\t%s -> %s  [label = "%s"];' % (s0, s1, string.replace(labelString(label), '\n', '\\n')));
        output.append('}');
        return string.join(output, '\n')
    
    def view(self):
        view(self.toDotString())


#
# Recognizers for special-case languages
#

NULL_FSA = FSA([0], None, [], 0, [])
EMPTY_STRING_FSA = FSA([0], None, [], 0, [0])
UNIVERSAL_FSA = FSA([0], None, [(0, 0, ANY)], 0, [0])

#
# Utility functions
#

def removeDuplicates(sequence):
    result = []
    for x in sequence:
        if x not in result:
            result.append(x)
    return result

def toFSA(arg):
    if hasattr(arg, 'isFSA') and arg.isFSA:
        return arg
    else:
        return singleton(arg)

def view(str):
    import os, tempfile
    dotfile = tempfile.mktemp()
    psfile = tempfile.mktemp()
    open(dotfile, 'w').write(str)
    dotter = 'dot'
    psviewer = 'gv'
    psoptions = '-antialias'
    os.system("%s -Tps %s -o %s" % (dotter, dotfile, psfile))
    os.system("%s %s %s&" % (psviewer, psoptions, psfile))


#
# Operations on languages (via their recognizers)
# These generally return nondeterministic FSAs.
#

def closure(arg):
    fsa = toFSA(arg)
    states, alpha, transitions, initial, finals = fsa.tuple()
    final = fsa.nextAvailableState()
    transitions = transitions[:]
    for s in finals:
        transitions.append((s, final, None))
    transitions.append((initial, final, None))
    transitions.append((final, initial, None))
    return fsa.create(states + [final], alpha, transitions, initial, [final], fsa.getArcMetadata())

def complement(arg):
    """Returns an FSA that accepts exactly those strings that the argument does
    not."""
    return toFSA(arg).complement()

def concatenation(a, *args):
    """Returns an FSA that accepts the language consisting of the concatenation
    of strings recognized by the arguments."""
    a = toFSA(a)
    for b in args:
        b = toFSA(b).sorted(a.nextAvailableState())
        states0, alpha0, transitions0, initial0, finals0 = a.tuple()
        states1, alpha1, transitions1, initial1, finals1 = b.tuple()
        a = a.create(states0 + states1, alpha0, transitions0 + transitions1 + list(map(lambda  s0, s1=initial1:(s0, s1, EPSILON), finals0)), initial0, finals1, a.getArcMetadata() + b.getArcMetadata())
    return a

def containment(arg, occurrences=1):
    """Returns an FSA that matches sequences containing at least _count_
    occurrences
    of _symbol_."""
    arg = toFSA(arg)
    fsa = closure(singleton(ANY))
    for i in range(occurrences):
        fsa = concatenation(fsa, concatenation(arg, closure(singleton(ANY))))
    return fsa

def difference(a, b):
    """Returns an FSA that accepts those strings accepted by the first
    argument, but not the second."""
    return intersection(a, complement(b))

def equivalent(a, b):
    """Return true ifff a and b accept the same language."""
    return difference(a, b).isEmpty() and difference(b, a).isEmpty()

def intersection(a, b):
    """Returns the intersection of two FSAs"""
    a, b = completion(a.determinized()), completion(b.determinized())
    states0, alpha0, transitions0, start0, finals0 = a.tuple()
    states1, alpha1, transitions1, start1, finals1 = b.tuple()
    states = [(start0, start1)]
    index = 0
    transitions = []
    arcMetadata = []
    buildArcMetadata = a.hasArcMetadata() or b.hasArcMetadata()
    while index < len(states):
        state, index = states[index], index + 1
        for sa0, sa1, la in a.transitionsFrom(state[0]):
            for sb0, sb1, lb in b.transitionsFrom(state[1]):
                label = labelIntersection(la, lb)
                if label:
                    s = (sa1, sb1)
                    transition = (state, s, label)
                    transitions.append(transition)
                    if s not in states:
                        states.append(s)
                    if buildArcMetadata:
                        if a.getArcMetadataFor((sa0, sa1, la)):
                            arcMetadata.append((transition, a.getArcMetadataFor((sa0, sa1, la))))
                        if b.getArcMetadataFor((sa0, sa1, la)):
                            arcMetadata.append((transition, b.getArcMetadataFor((sa0, sa1, la))))
    finals = list(filter(lambda s0, s1, f0=finals0, f1=finals1:s0 in f0 and s1 in f1, states))
    return a.create(states, alpha0, transitions, states[0], finals, arcMetadata).sorted()

def iteration(fsa, min=1, max=None):
    """
    ### equivalent(iteration(singleton('a', 0, 2)), compileRE('|a|aa'))
    ### equivalent(iteration(singleton('a', 1, 2)), compileRE('a|aa'))
    ### equivalent(iteration(singleton('a', 1)), compileRE('aa*'))
    """
    if min:
        return concatenation(fsa, iteration(fsa, min=min - 1, max=(max and max - 1)))
    elif max:
        return option(concatenation(fsa), iteration(fsa, min=min, max=max - 1))
    else:
        return closure(fsa)

def option(fsa):
    return union(fsa, EMPTY_STRING_FSA)

def reverse(fsa):
    states, alpha, transitions, initial, finals = fsa.tuple()
    newInitial = fsa.nextAvailableState()
    return fsa.create(states + [newInitial], alpha, list(map(lambda s0, s1, l:(s1, s0, l), transitions)) + list(map(lambda s1, s0=newInitial:(s0, s1, EPSILON), finals)), [initial])

def union(*args):
    initial, final = 1, 2
    states, transitions = [initial, final], []
    arcMetadata = []
    for arg in args:
        arg = toFSA(arg).sorted(reduce(max, states) + 1)
        states1, alpha1, transitions1, initial1, finals1 = arg.tuple()
        states.extend(states1)
        transitions.extend(list(transitions1))
        transitions.append((initial, initial1, None))
        for s in finals1:
            transitions.append((s, final, None))
        arcMetadata.extend(arg.getArcMetadata())
    if len(args):
        return toFSA(args[0]).create(states, alpha1, transitions, initial, [final], arcMetadata)
    else:
        return FSA(states, alpha1, transitions, initial, [final])


#
# FSA Functions
#

def completion(fsa):
    """Returns an FSA that accepts the same language as the argument, but that
    lands in a defined state for every input."""
    states, alphabet, transitions, start, finals = fsa.tuple()
    transitions = transitions[:]
    sinkState = fsa.nextAvailableState()
    for state in states:
            labels = list(map(lambda _, __, label:label, fsa.transitionsFrom(state)))
            for label in complementLabelSet(labels, alphabet):
                transitions.append(state, sinkState, label)
    if alphabet:
        transitions.extend(list(map(lambda symbol, s=sinkState:(s, s, symbol), alphabet)))
    else:
        transitions.append((sinkState, sinkState, ANY))
    return fsa.copy(states + [sinkState], alphabet, transitions, start, finals, fsa.getArcMetadata())

def determinize(fsa):
    return fsa.determinized()

def minimize(fsa):
    return fsa.minimized()

def sort(fsa):
    return fsa.sorted()

def trim(fsa):
    return fsa.trimmed()


#
# Label operations
#

TRACE_LABEL_OPERATIONS = 0

def labelComplements(label, alphabet):
    complement = labelComplement(label, alphabet) or []
    if TRACE_LABEL_OPERATIONS:
        print('complement(%s) = %s' % (label, complement))
    if  type(complement) != list:
        complement = [complement]
    return complement

def labelComplement(label, alphabet):
    if hasattr(label, 'complement'): # == InstanceType:
        return label.complement()
    elif alphabet:
        return list(filter(lambda s, s1=label:s != s1, alphabet))
    elif label == ANY:
        return None
    else:
        return symbolComplement(label)

def labelIntersection(l1, l2):
    intersection = _labelIntersection(l1, l2)
    if TRACE_LABEL_OPERATIONS:
            print('intersection(%s, %s) = %s' % (l1, l2, intersection))
    return intersection

def _labelIntersection(l1, l2):
    if l1 == l2:
        return l1
    #todo: is the following ever true
    elif not l1 or not l2:
        return None
    elif l1 == ANY:
        return l2
    elif l2 == ANY:
        return l1
    elif hasattr(l1, 'intersection'): 
        return l1.intersection(l2)
    elif hasattr(l2, 'intersection'): 
        return l2.intersection(l1)
    else:
        return symbolIntersection(l1, l2)

def labelString(label):
    return str(label)

def labelMatches(label, input):
    if hasattr(label, 'matches'): 
        return label.matches(input)
    else:
        return label == input


#
# Label set operations
#

TRACE_LABEL_SET_OPERATIONS = 0

def complementLabelSet(labels, alphabet=None):
    if not labels:
        return alphabet or [ANY]
    result = labelComplements(labels[0], alphabet)
    for label in labels[1:]:
        result = intersectLabelSets(labelComplements(label, alphabet), result)
    if TRACE_LABEL_SET_OPERATIONS:
        print('complement(%s) = %s' % (labels, result))
    return result

def intersectLabelSets(alist, blist):
    clist = []
    for a in alist:
        for b in blist:
            c = labelIntersection(a, b)
            if c:
                clist.append(c)
    if TRACE_LABEL_SET_OPERATIONS:
        print('intersection%s = %s' % ((alist, blist), clist))
    return clist

def unionLabelSets(alist, blist, alphabet=None):
    result = complementLabelSet(intersectLabelSets(complementLabelSet(alist, alphabet), complementLabelSet(blist, alphabet)), alphabet)
    if TRACE_LABEL_SET_OPERATIONS:
        print('union%s = %s' % ((alist, blist), result))
    return result


#
# Transition and Label utility operations
#

TRACE_CONSOLIDATE_TRANSITIONS = 0
TRACE_CONSTRUCT_LABEL_MAP = 0

def consolidateTransitions(transitions):
    result = []
    for s0, s1 in removeDuplicates(list(map(lambda s:(s[0],s[1]), transitions))):
        labels = []
        for ss0, ss1, label in transitions:
            if ss0 == s0 and ss1 == s1:
                labels.append(label)
        if len(labels) > 1:
            reduced = reduce(unionLabelSets, [[label] for label in labels])
            if TRACE_LABEL_OPERATIONS or TRACE_CONSOLIDATE_TRANSITIONS:
                print('consolidateTransitions(%s) -> %s' % (labels, reduced))
            labels = reduced
        for label in labels:
            result.append((s0, s1, label))
    return result

def constructLabelMap(labels, alphabet, includeComplements=0):
    """Return a list of (newLabel, positives), where newLabel is an
    intersection of elements from labels and their complemens, and positives is
    a list of labels that have non-empty intersections with newLabel."""
    label = labels[0]
    #if hasattr(label, 'constructLabelMap'):
    #   return label.constructLabelMap(labels)
    complements = labelComplements(label, alphabet)
    if len(labels) == 1:
        results = [(label, [label])]
        if includeComplements:
            for complement in complements:
                results.append((complement, []))
        return results
    results = []
    for newLabel, positives in constructLabelMap(labels[1:], alphabet, includeComplements=1):
        newPositive = labelIntersection(label, newLabel)
        if newPositive:
            results.append((newPositive, [label] + positives))
        for complement in complements:
            if positives or includeComplements:
                newNegative = labelIntersection(complement, newLabel)
                if newNegative:
                    results.append((newNegative, positives))
    if TRACE_CONSTRUCT_LABEL_MAP:
        print('consolidateTransitions(%s) -> %s' % (labels, results))
    return results


#
# Symbol operations
#

def symbolComplement(symbol):
    if '&' in symbol:
        import string
        return list(map(symbolComplement, string.split(symbol, '&')))
    elif symbol[0] == '~':
        return symbol[1:]
    else:
        return '~' + symbol

def symbolIntersection(s1, s2):
    import string
    set1 = string.split(s1, '&')
    set2 = string.split(s2, '&')
    for symbol in set1:
        if symbolComplement(symbol) in set2:
            return None
    for symbol in set2:
        if symbol not in set1:
            set1.append(symbol)
    nonNegatedSymbols = [s for s in set1 if s[0] != '~']
    if len(nonNegatedSymbols) > 1:
        return None
    if nonNegatedSymbols:
        return nonNegatedSymbols[0]
    set1.sort()
    return string.join(set1, '&')


#
# Construction from labels
#

def singleton(symbol, alphabet=None, arcMetadata=None):
    fsa = FSA([0,1], alphabet, [(0, 1, symbol)], 0, [1])
    if arcMetadata:
        fsa.setArcMetadataFor((0, 1, symbol), arcMetadata)
    fsa.label = str(symbol)
    return fsa

def sequence(sequence, alphabet=None):
    fsa = reduce(concatenation, list(map(lambda label, alphabet=alphabet:singleton(label, alphabet), sequence)), EMPTY_STRING_FSA)
    fsa.label = str(sequence)
    return fsa


#
# Compiling Regular Expressions
#

def compileRE(s, **options):
    import string
    if not options.get('multichar'):
        s = string.replace(s, ' ', '')
    fsa, index = compileREExpr(s + ')', 0, options)
    if index < len(s):
        raise 'extra ' + str(')')
    fsa.label = str(s)
    return fsa.minimized()

def compileREExpr(str, index, options):
    fsa = None
    while index < len(str) and str[index] != ')':
        fsa2, index = compileConjunction(str, index, options)
        if  str[index] == '|': index = index + 1
        fsa = (fsa and union(fsa, fsa2)) or fsa2
    return (fsa or EMPTY_STRING_FSA), index

def compileConjunction(str, index, options):
    fsa = UNIVERSAL_FSA
    while str[index] not in ')|':
        conjunct, index = compileSequence(str, index, options)
        if  str[index] == '&': index = index + 1
        fsa = intersection(fsa, conjunct)
    return fsa, index

def compileSequence(str, index, options):
    fsa = EMPTY_STRING_FSA
    while str[index] not in ')|&':
        fsa2, index = compileItem(str, index, options)
        fsa = concatenation(fsa, fsa2)
    return fsa, index

def compileItem(str, index, options):
    c , index = str[index], index + 1
    while c == ' ':
        c, index = str[index], index + 1
    if c == '(':
        fsa, index = compileREExpr(str, index, options)
        assert str[index] == ')'
        index = index + 1
    elif c == '.':
        fsa = singleton(ANY)
    elif c == '~':
        fsa, index = compileItem(str, index, options)
        fsa = complement(fsa)
    else:
        label = c
        if options.get('multichar'):
            import string
            while str[index] in string.letters or str[index] in string.digits:
                label, index = label + str[index], index + 1
        if str[index] == ':':
            index = index + 1
            upper = label
            lower, index = str[index], index + 1
            if upper  == '0':
                upper  = EPSILON
            if lower == '0':
                lower = EPSILON
            label = (upper, lower)
        fsa = singleton(label)
    while str[index] in '?*+':
        c, index = str[index], index + 1
        if c == '*':
            fsa = closure(fsa)
        elif c == '?':
            fsa = union(fsa, EMPTY_STRING_FSA)
        elif c == '+':
            fsa = iteration(fsa)
        else:
            raise ValueError('Unimplemented')
    return fsa, index

"""
TRACE_LABEL_OPERATIONS = 1
TRACE_LABEL_OPERATIONS = 0

print compileRE('')
print compileRE('a')
print compileRE('ab')
print compileRE('abc')
print compileRE('ab*')
print compileRE('a*b')
print compileRE('ab*c')
print compileRE('ab?c')
print compileRE('ab+c')
print compileRE('ab|c')
print compileRE('a(b|c)')

print compileRE('abc').accepts('abc')
print compileRE('abc').accepts('ab')

print singleton('1', alphabet=['1']).minimized()
print complement(singleton('1')).minimized()
print singleton('1', alphabet=['1'])
print completion(singleton('1'))
print completion(singleton('1', alphabet=['1']))
print complement(singleton('1', alphabet=['1']))
print complement(singleton('1', alphabet=['1', '2']))
print complement(singleton('1', alphabet=['1', '2'])).minimized()

print intersection(compileRE('a*b'), compileRE('ab*'))
print intersection(compileRE('a*cb'), compileRE('acb*'))
print difference(compileRE('ab*'), compileRE('abb')).minimized()

print compileRE('n.*v.*n')
print compileRE('n.*v.*n&.*n.*n.*n.*')

print intersection(compileRE('n.*v.*n'), compileRE('.*n.*n.*n.*'))
print difference(compileRE('n.*v.*n'), compileRE('.*n.*n.*n.*'))
print difference(difference(compileRE('n.*v.*n'), compileRE('.*n.*n.*n.*')), compileRE('.*v.*v.*'))

print compileRE('a|~a').minimized()


print containment(singleton('a'), 2).minimized()
print difference(containment(singleton('a'), 2), containment(singleton('a'), 3)).minimized()
print difference(containment(singleton('a'), 3), containment(singleton('a'), 2)).minimized()

print difference(compileRE('a*b'), compileRE('ab*')).minimized()

"""
