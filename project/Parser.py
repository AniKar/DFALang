import Scanner
from Scanner import Token as T

import Automaton
import threading

class SyntaxError(Exception):
    def __init__(self, mes):
        self.message = mes

class RuntimeError(Exception):
    def __init__(self, mes):
        self.message = mes

#***Special types used for parsing***#

# constant (automaton)
class DFA:
    def __init__(self, dfa):
        self.dfa = dfa

    def evaluate(self, env):
        return self.dfa

    def __str__(self):
        return str(self.dfa)

# variable
class Variable:
    def __init__(self, name):
        self.name = name

    def evaluate(self, env):
        if self.name in env:
            return env[self.name].evaluate(env)
        else:
            raise RuntimeError("No variable named " + self.name)

    def __str__(self):
        return self.name

# DFA definition
class DFADefiniton:
    def __init__(self, name, dfa):
        self.name = name
        self.dfa = dfa

    def execute(self, env):
        automaton = self.dfa.evaluate(env)
        if automaton.check():
            env[self.name] = self.dfa
            print("Defined automaton " + self.name + " = " + str(automaton))
        else:
            raise RuntimeError("Invalid automaton definition " + self.name)

class PrintDFAList:
    def __init__(self, modules = []):
        self.modules = modules

    def addModule(self, module):
        self.modules.append(module)

    def execute(self, env):
        for module in self.modules:
            module.execute(env)

class PrintDFA:
    def __init__(self, dfa):
        self.dfa = dfa

    def execute(self, env):
        automaton = self.dfa.evaluate(env)
        automaton.show(self.dfa.name)

# sequence of modules
class ModuleSequence:
    def __init__(self, modules = []):
        self.modules = modules

    def addModule(self, module):
        self.modules.append(module)

    def execute(self, env):
        for module in self.modules:
            module.execute(env)

# accept statement with single automaton
class SimpleAccept:
    def __init__(self, string, dfa):
        self.string = string
        self.dfa = dfa

    def execute(self, env):
        automaton = self.dfa.evaluate(env)
        if not automaton.check():
            raise RuntimeError("Invalid automaton definition")

        if automaton.acceptsString(self.string):
            print("String {} is accepted with the automaton {}".format(self.string, self.dfa))
        else:
            print("String {} is not accepted with the automaton {}".format(self.string, self.dfa))


class AcceptStringThread(threading.Thread):
   def __init__(self, module, env):
       threading.Thread.__init__(self)
       self.module = module
       self.env = env

   def run(self):
       self.module.execute(self.env)

# accept statement with multiple automata
class ComplexAccept:
    def __init__(self, simple_modules = []):
        self.simple_modules = simple_modules

    def addModule(self, module):
        self.simple_modules.append(module)

    def execute(self, env):
        # execute the simple accept statements in parallel
        threads = []
        for module in self.simple_modules:
            thread = AcceptStringThread(module, env)
            threads.append(thread)

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


#****************************Parser******************************#
# Parser is implemented with "predictive parsing" top-down method.
class Parser:
    def __init__(self, file):
        with open(file, 'r') as source:
            text = source.read()

        self.__scan = Scanner.Scanner(text)
        self.__lookahead = (None, None, None)
        self.__module_seq = ModuleSequence()

    # current line number
    def __currentLine(self):
        return self.__scan.line

    # next lexeme
    def __nextLexeme(self):
        return self.__lookahead[0]

    # check next token type
    def __nextTokenIs(self, token):
        return token == self.__lookahead[1]

    # get the next token
    def __getNext(self):
        self.__lookahead = self.__scan.next()
        self.__checkValidLexeme()

    # check for a lexical error
    def __checkValidLexeme(self):
        if not self.__lookahead:
            msg = "Unexpected symbol near line {}".format(self.__currentLine())
            raise SyntaxError(msg)

    # match the current token with the expected one
    def __match(self, token):
        if self.__nextTokenIs(token):
            self.__getNext()
        else:
            msg = "Expected {}, but got {} near line {}".\
                        format(token, self.__lookahead[1], self.__currentLine())
            raise SyntaxError(msg)

    # add a new module to the sequence
    def __addModule(self, module):
        self.__module_seq.addModule(module)

    # module sequence
    def moduleSequence(self):
        return self.__module_seq


    def parse(self):
        if self.__nextTokenIs(T.Eof):
            return True
        try:
            # start parsing
            if not self.__lookahead[0]:
                self.__getNext()

            # parse the leading new lines
            if self.__nextTokenIs(T.Eol):
                self.parseNewLines()

            # parse a single module
            if self.__nextTokenIs(T.Ident):
                module = self.parseDefinition()
            elif self.__nextTokenIs(T.Accept):
                module = self.parseStringAccept()
            else:
                assert(self.__nextTokenIs(T.Print))
                module = self.parsePrint()

            self.__addModule(module)
            # modules must be separated by new lines
            self.parseNewLines()
        except SyntaxError as se:
            print(se)
            return False

        # parse the rest of the modules recursively
        return self.parse()

    # parse automaton definition module
    def parseDefinition(self):
        name = self.__nextLexeme()
        self.__match(T.Ident)
        self.__match(T.Define)
        dfa = self.parseAutomaton()
        return DFADefiniton(name, dfa)

    # parse string accepting module
    def parseStringAccept(self):
        self.__match(T.Accept)
        # match the string to accept
        string = self.parseString()
        self.__match(T.With)

        # single automaton given with identifier
        if self.__nextTokenIs(T.Ident):
            dfa = Variable(self.__nextLexeme())
            self.__match(T.Ident)
            module = SimpleAccept(string, dfa)

        # single automaton given with inline definition
        elif self.__nextTokenIs(T.Automaton):
            dfa = self.parseAutomaton()
            module = SimpleAccept(string, dfa)

        # multiple automata given with an identifier list
        else:
            self.__match(T.LCurlyBr)

            module = ComplexAccept()
            dfa = Variable(self.__nextLexeme())
            self.__match(T.Ident)
            module.addModule(SimpleAccept(string, dfa))

            while not self.__nextTokenIs(T.RCurlyBr):
                self.__match(T.Comma)
                dfa = Variable(self.__nextLexeme())
                self.__match(T.Ident)
                module.addModule(SimpleAccept(string, dfa))
            self.__match(T.RCurlyBr)

        return module

    # parse automaton definition body
    def parseAutomaton(self):
        self.__match(T.Automaton)
        self.__match(T.LCurlyBr)

        state_count = self.parseStates()
        alphabet = self.parseAlphabet()
        transitions = self.parseTransitionList()
        accept_states = self.parseAcceptStates()

        self.__match(T.RCurlyBr)

        dfa = Automaton.Automaton(state_count, alphabet,
                                  transitions, accept_states)
        return DFA(dfa)

    # parse the state count
    def parseStates(self):
        self.__match(T.States)
        self.__match(T.Define)

        state_count = self.parseNumber()
        return state_count

    # parse the alphabet
    def parseAlphabet(self):
        self.__match(T.Alphabet)
        self.__match(T.Define)

        alphabet = []
        self.__match(T.LCurlyBr)
        l = self.parseLetter()
        alphabet.append(l)

        while not self.__nextTokenIs(T.RCurlyBr):
            self.__match(T.Comma)
            l = self.parseLetter()
            alphabet.append(l)
        self.__match(T.RCurlyBr)

        return alphabet

    # parse the transitions
    def parseTransitionList(self):
        self.__match(T.Transitions)
        self.__match(T.Define)

        transitions = {}
        self.__match(T.LCurlyBr)
        tr = self.parseTransition()
        transitions[(tr[0], tr[1])] = tr[2]

        while not self.__nextTokenIs(T.RCurlyBr):
            self.__match(T.Comma)
            tr = self.parseTransition()
            if (tr[0], tr[1]) in transitions:
                print("Warning: Non deterministic transition list definition! " \
                      "Out of conflicting transitions the last one will be considered.")
            transitions[(tr[0], tr[1])] = tr[2]
        self.__match(T.RCurlyBr)

        return transitions

    # parse a single transition
    def parseTransition(self):
        self.__match(T.LRoundBr)

        state1 = self.parseNumber()
        self.__match(T.Comma)

        input = self.parseLetter()
        self.__match(T.Comma)

        state2 = self.parseNumber()
        self.__match(T.RRoundBr)

        return (state1, input, state2)

    # parse the accept states
    def parseAcceptStates(self):
        self.__match(T.AcceptStates)
        self.__match(T.Define)

        accept_states = []
        self.__match(T.LCurlyBr)
        s = self.parseNumber()
        accept_states.append(s)

        while not self.__nextTokenIs(T.RCurlyBr):
            self.__match(T.Comma)
            s = self.parseNumber()
            accept_states.append(s)
        self.__match(T.RCurlyBr)

        return accept_states

    # parse Automaton printing command
    def parsePrint(self):
        self.__match(T.Print)
        if self.__nextTokenIs(T.Ident):
            dfa = Variable(self.__nextLexeme())
            self.__match(T.Ident)
            module = PrintDFA(dfa)
        else:
            self.__match(T.LCurlyBr)
            module = PrintDFAList()
            dfa = Variable(self.__nextLexeme())
            self.__match(T.Ident)
            module.addModule(PrintDFA(dfa))

            while not self.__nextTokenIs(T.RCurlyBr):
                self.__match(T.Comma)
                dfa = Variable(self.__nextLexeme())
                self.__match(T.Ident)
                module.addModule(PrintDFA(dfa))
            self.__match(T.RCurlyBr)
        return module

    # parse a string
    def parseString(self):
        str = self.__nextLexeme()
        self.__match(T.String)
        # remove the first and last quotes
        return str[1:-1] # "abc" -> abc

    # parse a letter
    def parseLetter(self):
        l = self.__nextLexeme()
        self.__match(T.Letter)
        return l[1] # 'a' -> a

    # parse a number
    def parseNumber(self):
        n = int(self.__nextLexeme())
        self.__match(T.Number)
        return n

    # parse new lines
    def parseNewLines(self):
        self.__match(T.Eol)
        while self.__nextTokenIs(T.Eol):
            self.__getNext()
            
