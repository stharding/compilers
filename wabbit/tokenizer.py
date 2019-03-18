# tokenizer.py
r'''
Project 1 - Write a Lexer
=========================
In the first project, you are going to write a simple lexer for a
subset of the Wabbit language.  The project is described in comments
and documentation within this file.  Please read the complete
contents of this file and carefully complete the steps indicated.

Overview:
---------
The process of lexing is that of taking input text and breaking it
down into a stream of tokens. Each token is like a valid word from the
dictionary.  Essentially, the role of the lexer is to make sure
that the input text consists of valid symbols and tokens prior to any
further processing related to parsing.

Each token is defined by a regular expression.  Thus, your primary task
in this first project is to define a set of regular expressions for
the language.  The actual job of lexing will be handled by SLY
(https://github.com/dabeaz/sly)

Specification:
--------------
Your lexer must recognize the following symbols and tokens.  The name
on the left is the token name, the value on the right is the matching
text.  Note: Additional features will be added in later projects.

Reserved Keywords:
    CONST   : 'const'
    VAR     : 'var'
    PRINT   : 'print'

Identifiers (Same rules as for Python):
    ID      : Text starting with a letter or '_', followed by any number
              number of letters, digits, or underscores.
              Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

Operators and Delimiters:
    PLUS     : '+'
    MINUS    : '-'
    TIMES    : '*'
    DIVIDE   : '/'
    ASSIGN   : '='
    SEMI     : ';'
    LPAREN   : '('
    RPAREN   : ')'
    GROW     : '^'
    DEREF    : '`'    (Backtick)

Literals:
    INTEGER :  123   (decimal)

    FLOAT   : 1.234
              .1234
              1234.

    CHAR    : 'a'     (a single character - byte)
              '\xhh'  (byte value)

Comments:  To be ignored by your lexer
     //             Skips the rest of the line
     /* ... */      Skips a block (no nesting allowed)

Errors: Your lexer may optionally recognize and report the following
error messages:

     lineno: Illegal char 'c'
     lineno: Unterminated string
     lineno: Unterminated comment

Testing
-------
To get started, look at Tests/lextest[0-5].wb.  Work through each file
in sequence.  Run your tokenize like this:

     bash % python3 -m wabbit.tokenizer lextest0.wb
     bash % python3 -m wabbit.tokenizer lextest1.wb
     bash % python3 -m wabbit.tokenizer lextest2.wb
     bash % python3 -m wabbit.tokenizer lextest3.wb
     bash % python3 -m wabbit.tokenizer lextest4.wb
     bash % python3 -m wabbit.tokenizer lextest5.wb

Bonus: How would you go about turning these tests into proper unit tests?
'''

# ----------------------------------------------------------------------
# The following import loads a function error(lineno, msg) that should be
# used to report all error messages issued by your lexer.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# -----------------------------------------------------------------------
# The SLY package. https://github.com/dabeaz/sly
from sly import Lexer

# -----------------------------------------------------------------------
# Lexers are defined by a class that inherits from sly.Lexer.  Follow
# the instructions contained in the class below.

class WabbitLexer(Lexer):
    # ----------------------------------------------------------------------
    # Token set. This set identifies the complete list of token names
    # to be recognized by your lexer.  Do not change any of these names.
    tokens = {
        # Identifiers and keywords
        ID, PRINT, VAR, CONST,

        # Literals
        INTEGER, FLOAT, CHAR,

        # Operators and delimiters
        PLUS, MINUS, TIMES, DIVIDE,

        # Delimiters and other symbols
        ASSIGN, LPAREN, RPAREN, SEMI,

        # Memory operators
        GROW, DEREF,
    }

    # ----------------------------------------------------------------------
    # Ignored characters (whitespace)
    #
    # The following characters are ignored completely by the lexer.
    # Do not change.
    ignore = ' \t\r'

    # ----------------------------------------------------------------------
    # Ignored patterns.  Fill in the regexs below to ignore comments.
    # You should do this as one of the first steps in your solution.
    # Most of the test files contain comments and you need to make sure
    # they're being ignored.

    # Block-style comment (/* ... */)
    @_(r'you write')
    def COMMENT(self, t):
        self.lineno += t.value.count('\n')

    # Line-style comment (//...)
    @_(r'you write')
    def CPPCOMMENT(self, t):
        self.lineno += 1

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : write the regexs indicated below ***
    #
    # Tokens for simple symbols: + - * / = ( ) ; ^ ` etc.
    #
    # Caution: Definition order matters. Longer symbols should appear
    # before shorter symbols that are a substring (for example, the
    # pattern for '==' should go before '=').

    PLUS      = r'+'
    MINUS     = r'-'
    TIMES     = r'*'
    DIVIDE    = r'/'
    SEMI      = r';'
    LPAREN    = r'('
    RPAREN    = r')'
    ASSIGN    = r'='
    GROW      = r'^'
    DEREF     = r'^'

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : write the regexs and additional code below ***
    #
    # Tokens for literals, INTEGER, FLOAT, STRING.

    # Floating point constant.   You must recognize floating point numbers in
    # the following formats:
    #
    #   1.23
    #   123.
    #   .123
    #
    # Bonus: Recognize floating point numbers in scientific notation
    #
    #   1.23e1
    #   1.23e+1
    #   1.23e-1
    #   1e1

    FLOAT = r'you write'

    # Integer literal
    #
    #     1234             (decimal)
    #
    # Bonus: Recognize integers in different bases such as 0x1a, 0o13 or 0b111011.

    INTEGER = r'you write'

    # Character constant. You must recognize a single letter enclosed in single quotes
    # For example:
    #
    #     'a'
    #
    # Escape codes should also be be recognized:
    #
    #     '\n'    - Newline
    #     '\\'    - Backslash
    #     '\''    - Quote
    #     '\xhh'  - Generic byte

    CHAR = r"you write"

    # ----------------------------------------------------------------------
    # *** YOU MUST COMPLETE : Write the regex and add keywords ***
    #
    # Identifiers and keywords.
    #
    # Match a raw identifier.  Identifiers follow the same rules as Python.
    # That is, they start with a letter or underscore (_) and can contain
    # an arbitrary number of letters, digits, or underscores after that.
    # Language keywords such as "print" and "var" are also matched as
    # identifiers. You need to catch these and change their token type
    # to match the appropriate keyword.

    ID = 'you write'

    # The following assignments are declaring special cases. If the
    # matched text of ID exactly matches the text in [...], the
    # token type is changed to the value on the right.

    ID['print'] = PRINT

    # ----------------------------------------------------------------------
    # Method that ignores one or more newlines and increments the line number
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # ----------------------------------------------------------------------
    # Bad character error handling
    def error(self, t):
        error(self.lineno,"Illegal character %r" % t.value[0])
        self.index += 1

# ----------------------------------------------------------------------
#                DO NOT CHANGE ANYTHING BELOW THIS PART
#
# Use this main program to test/debug your lexer.  Run it using the -m option
#
#    bash % python3 -m wabbit.tokenizer filename.wb
#
# ----------------------------------------------------------------------
def main():
    '''
    Main program. For debugging purposes.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m wabbit.tokenizer filename\n")
        raise SystemExit(1)

    lexer = WabbitLexer()
    text = open(sys.argv[1]).read()
    for tok in lexer.tokenize(text):
        print(tok)

if __name__ == '__main__':
    main()
