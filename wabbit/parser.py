# parser.py
'''
Project 2:  Write a parser
==========================
In this project, you write the basic shell of a parser for Wabbit.  A
formal BNF of the language follows.  Your task is to write parsing
rules and build the AST for this grammar using SLY.  The following
grammar is partial for the entire project.  More features get added in
later projects.

program : statements
        | empty

statements :  statements statement
           |  statement

statement :  const_declaration
          |  var_declaration
          |  assign_statement
          |  print_statement

const_declaration : CONST ID = expression ;

var_declaration : VAR ID datatype ;
                | VAR ID datatype = expression ;

assign_statement : location = expression ;

print_statement : PRINT expression ;

expression : + expression
           | - expression
           | ^ expression
           | expression + expression
           | expression - expression
           | expression * expression
           | expression / expression
           | ( expression )
           | location
           | typecast
           | literal

typecast  : datatype ( expression )
          ;

literal : INTEGER
        | FLOAT
        | CHAR

location : simplelocation
         | memorylocation
         ;

simplelocation : ID
         ;

memorylocation : ` expression
         ;

datatype : ID
         ;

empty    :

To do the project, follow the instructions contained in comments below.
'''

# ----------------------------------------------------------------------
# parsers are defined using SLY.  You inherit from the Parser class
#
# See http://sly.readthedocs.io/en/latest/
# ----------------------------------------------------------------------
from sly import Parser

# ----------------------------------------------------------------------
# The following import loads a function error(lineno,msg) that should be
# used to report all error messages issued by your parser.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# ----------------------------------------------------------------------
# Import the lexer class.  It's token list is needed to validate and
# build the parser object.
from .tokenizer import WabbitLexer
from . import typesys

# ----------------------------------------------------------------------
# Get the AST nodes.
# Read further instructions in ast.py
from .ast import *

class WabbitParser(Parser):

    # Same token set as defined in the lexer
    tokens = WabbitLexer.tokens

    # ----------------------------------------------------------------------
    # Operator precedence table.   Operators must follow the same
    # precedence rules as in Python.  Instructions to be given in the project.

    precedence = (
    )

    # ----------------------------------------------------------------------
    # YOUR TASK.   Translate the BNF in the string below into a collection
    # of parser functions.  For example, a rule such as :
    #
    #   program : statements
    #
    # Gets turned into a Python method like this:
    #
    # @_('statements')
    # def program(self, p):
    #      return Program(p.statements)
    #
    # For symbols such as '(' or '+', you'll need to replace with the name
    # of the corresponding token such as LPAREN or PLUS.
    #
    # In the body of each rule, create an appropriate AST node and return it
    # as shown above.
    #
    # STARTING OUT
    # ============
    # The following grammar rules should give you an idea of how to start.
    # Try running this file on the input Tests/parsetest0.wb
    #
    # Afterwards, add features by looking at the code in Tests/parsetest0-7.wb

    @_('statements')
    def program(self, p):
         return Program(p.statements)

    @_('statement')
    def statements(self, p):               # A single statement
        return [p.statement]               # The initial list

    @_('statements statement')
    def statements(self, p):               # Multiple statements
        p.statements.append(p.statement)   # Add a statement to previous statements
        return p.statements

    @_('print_statement',
       'const_declaration',
       'var_declaration',
        # add more statements later
    )
    def statement(self, p):
        return p[0]

    @_('CONST ID ASSIGN expression SEMI')
    def const_declaration(self, p):
        return ConstDeclaration(p.ID, p.expression, lineno=p.lineno)

    @_('VAR ID datatype ASSIGN expression SEMI')
    def var_declaration(self, p):
        return VarDeclaration(p.ID, p.datatype, p.expression, lineno=p.lineno)

    @_('VAR ID datatype SEMI')
    def var_declaration(self, p):
        return VarDeclaration(p.ID, SimpleType(p.datatype, lineno=p.lineno), None, lineno=p.lineno)

    @_('ID')
    def datatype(self, p):
        return SimpleType(p.ID, lineno=p.lineno)

    @_('PRINT expression SEMI')
    def print_statement(self, p):
        print(t for t in p)
        return PrintStatement(p.expression, lineno=p.lineno)

    @_('datatype LPAREN expression RPAREN')
    def expression(self, p):
        return TypeCast(p.datatype, p.expression, lineno=p.lineno)

    @_('PLUS expression')
    def expression(self, p):
        return UnaryOp(p[0], p.expression, lineno=p.lineno)

    @_('expression PLUS expression')
    def expression(self, p):
        print(t for t in p)
        return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('MINUS expression')
    def expression(self, p):
        return UnaryOp(p[0], p.expression, lineno=p.lineno)

    @_('expression MINUS expression')
    def expression(self, p):
        return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('expression TIMES expression')
    def expression(self, p):
        return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('expression DIVIDE expression')
    def expression(self, p):
        return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    @_('LPAREN expression RPAREN')
    def expression(self, p):
        return p

    @_('literal')
    def expression(self, p):
        return p.literal

    @_('INTEGER')
    def literal(self, p):
        return IntegerLiteral(int(p.INTEGER), lineno=p.lineno)

    @_('FLOAT')
    def literal(self, p):
        return FloatLiteral(float(p.FLOAT), lineno=p.lineno)

    @_('CHAR')
    def literal(self, p):
        return CharLiteral(p.CHAR, lineno=p.lineno)

    # ----------------------------------------------------------------------
    # DO NOT MODIFY
    #
    # catch-all error handling.   The following function gets called on any
    # bad input.  p is the offending token or None if end-of-file (EOF).
    def error(self, p):
        if p:
            error(p.lineno, "Syntax error in input at token '%s'" % p.value)
        else:
            error('EOF','Syntax error. No more input.')

# ----------------------------------------------------------------------
#                     DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

def parse(source):
    '''
    Parse source code into an AST. Return the top of the AST tree.
    '''
    lexer = WabbitLexer()
    parser = WabbitParser()
    # print(list(lexer.tokenize(source)))
    ast = parser.parse(lexer.tokenize(source))
    return ast

def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m wabbit.parser filename\n')
        raise SystemExit(1)

    # Parse and create the AST
    ast = parse(open(sys.argv[1]).read())

    # Output the resulting parse tree structure
    for depth, node in flatten(ast):
        print('%s: %s%s' % (getattr(node, 'lineno', None), ' '*(4*depth), node))

if __name__ == '__main__':
    main()
