import enum
import re

# Types of lexemes
class Token(enum.Enum):
    Eof          = 1
    Number       = 2
    String       = 3
    Ident        = 4
    Letter       = 5

    # keywords
    Automaton    = 6
    States       = 7
    Alphabet     = 8
    Transitions  = 9
    AcceptStates = 10
    Accept       = 11
    With         = 12
    Print        = 13

    # symbols
    LRoundBr     = 14
    RRoundBr     = 15
    LCurlyBr     = 16
    RCurlyBr     = 17
    Define       = 18
    Comma        = 19
    Eol          = 20
    SplitLn      = 21


class Scanner:
    # keywords
    __keywords = {
        'DFA'         : Token.Automaton,
        'S'           : Token.States,
        'States'      : Token.States,
        'A'           : Token.Alphabet,
        'Alphabet'    : Token.Alphabet,
        'T'           : Token.Transitions,
        'Transitions' : Token.Transitions,
        'F'           : Token.AcceptStates,
        'FinalStates' : Token.AcceptStates,
        'Accept'      : Token.Accept,
        'With'        : Token.With,
        'Print'       : Token.Print
    }
    # symbols
    __symbols = {
        '('  : Token.LRoundBr,
        ')'  : Token.RRoundBr,
        '{'  : Token.LCurlyBr,
        '}'  : Token.RCurlyBr,
        '='  : Token.Define,
        ','  : Token.Comma,
        '\n' : Token.Eol,
        '\\' : Token.SplitLn
    }

    def __init__(self, src):
        self.source = src + '\n' + '@'
        self.line = 1

        self.reComment = re.compile(r'^\#.*')
        self.reNumber  = re.compile(r'^[0-9]\d*')
        self.reString  = re.compile(r'^"[a-zA-Z]+"')
        self.reIdent   = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*')
        self.reLetter  = re.compile(r"^'[a-zA-Z]+'")
        self.reSymbols = re.compile(r'^[\(\)\{\},=\n\\]')


    def cutLexeme(self, ma):
        lexeme = ma.group(0)
        self.source = self.source[ma.end():]
        return lexeme


    def next(self):
        # remove the leading spaces/tabs
        k = 0
        while self.source[k] in ' \t':
            k += 1
        if k != 0:
            self.source = self.source[k:]

        # end of file
        if self.source[0] == '@':
            return ('EOF', Token.Eof, self.line)

        # match comment
        mo = self.reComment.match(self.source)
        if mo:
            self.source = self.source[mo.end():]
            return self.next()

        # match number (integer)
        mo = self.reNumber.match(self.source)
        if mo:
            lexeme = self.cutLexeme(mo)
            return (lexeme, Token.Number, self.line)

        # match string
        mo = self.reString.match(self.source)
        if mo:
            lexeme = self.cutLexeme(mo)
            return (lexeme, Token.String, self.line)

        # match identifier or keyword
        mo = self.reIdent.match(self.source)
        if mo:
            lexeme = self.cutLexeme(mo)
            token = self.__keywords.get(lexeme, Token.Ident)
            return (lexeme, token, self.line)

        # match letter
        mo = self.reLetter.match(self.source)
        if mo:
            lexeme = self.cutLexeme(mo)
            return (lexeme, Token.Letter, self.line)

        # match symbols
        mo = self.reSymbols.match(self.source)
        if mo:
            lexeme = self.cutLexeme(mo)
            token = self.__symbols[lexeme]
            # split line
            if '\\' == lexeme:
                assert(self.next()[1] == Token.Eol)
                return self.next()
            # new line
            if '\n' == lexeme:
                self.line += 1
            return (lexeme, token, self.line)

        return None
