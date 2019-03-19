# checker.py
'''
*** Do not start this project until you have fully completed Exercise 3. ***

Overview
--------
In this project you need to perform semantic checks on your program.
This problem is multifaceted and complicated.  To make it somewhat
less brain exploding, you need to take it slow and in small parts.
The basic gist of what you need to do is as follows:

1.  Names and symbols:

    All identifiers must be defined before they are used.  This
    includes variables, constants, and typenames.  For example, this
    kind of code generates an error:

       a = 3;              // Error. 'a' not defined.
       var a int;

2.  Types of literals and constants

    All literal symbols are implicitly typed and must be assigned a
    type of "int", "float", or "char".  This type is used to set
    the type of constants.  For example:

       const a = 42;         // Type "int"
       const b = 4.2;        // Type "float"
       const c = 'a';        // Type "char""

3.  Operator type checking

    Binary operators only operate on operands of a compatible type.
    Otherwise, you get a type error.  For example:

        var a int = 2;
        var b float = 3.14;

        var c int = a + 3;    // OK
        var d int = a + b;    // Error.  int + float
        var e int = b + 4.5;  // Error.  int = float

    In addition, you need to make sure that only supported 
    operators are allowed.  For example:

        var a char = 'a';        // OK
        var b char = 'a' + 'b';  // Error (unsupported op +)

    You'll also need to make type casts properly propagate the
    type:

        var c float = float(200) + 3.5;

4.  Assignment.

    The left and right hand sides of an assignment operation must be
    declared as the same type.

        var a int;
        a = 4 + 5;     // OK
        a = 4.5;       // Error. int = float

    Values can only be assigned to variable declarations, not
    to constants.

        var a int;
        const b = 42;

        a = 37;        // OK
        b = 37;        // Error. b is const

5.  Memory (CHALLENGE: Save until last).

    The memory operators ^ and ` are rather mind boggling. Reminder,
    The ^ is used to grow memory. The ` is used to refer to a specific
    memory location.

    The argument to both ^ and ` must be an integer.  The ^ operator
    takes an integer increment and returns an integer result.

    The ` operator always takes an integer argument which is the 
    memory address.  So, for type-checking, you need to verify that.
    The challenge concerns the result type of the ` operator.  ` is
    polymorphic--meaning that it can return any type.  However, the
    exact type can only be determined by surrounding context.  If
    the type can't be determined, it should default to char.
    Here are some examples:

      var x int = `1234;     // Type of (`) is int.  Reads an int. 
      var y float = `1234;   // Type of (`) is float.  Reads a float.

      `1234 = 42;            // Store an int at 1234.
      `1234 = 4.2;           // Store a float at 1234.
      `1234 = 'x';           // Store a byte 'x' at 1234.
  
      print `1234;           // Ok. Defaults to char.
      print `1234 + 0;       // Ok. Reads an int from 1234 (0 is an int)
      print `1234 + 0.0;     // Ok. Reads a float from 1234.

      `1234 = `4567;         // Copies a character from 4567 to 1234.

    Frankly, this is all a bit horrible. Essentially you're going to
    have to try and do your best to infer the result type of the `
    operator based on best available information from nearby parse tree
    nodes.  Some things are probably not going to work.

Implementation Strategy:
------------------------
You're going to use the NodeVisitor class defined in wabbit/ast.py to
walk the parse tree.   You will be defining various methods for
different AST node types.  For example, if you have a node BinOp,
you'll write a method like this:

      def visit_BinOp(self, node):
          ...

To start, make each method simply print out a message:

      def visit_BinOp(self, node):
          print('visit_BinOp:', node)
          self.visit(node.left)
          self.visit(node.right)

This will at least tell you that the method is firing.  Try some
simple code examples and make sure that all of your methods
are actually running when you walk the parse tree.

Testing
-------
The files Tests/checktest0-7.wb contain different things you need
to check for.  Specific instructions are given in each test file.

General thoughts and tips
-------------------------
The main thing you need to be thinking about with checking is program
correctness.  Does this statement or operation that you're looking at
in the parse tree make sense?  If not, some kind of error needs to be
generated.  Use your own experiences as a programmer as a guide (think
about what would cause an error in your favorite programming
language).

One challenge is going to be the management of many fiddly details. 
You've got to track symbols, types, and different sorts of capabilities.
It's not always clear how to best organize all of that.  So, expect to
fumble around a bit at first.

Also, when making a compiler, not everything is super clean to figure
out.  The silly memory dereferencing operator (`) in Wabbit is nothing
short of a major headache.  Who thought of that crazy thing?
'''

from .errors import error
from .ast import *
from .typesys import lookup_type, check_binary_op, check_unary_op
from collections import ChainMap

class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    '''
    def __init__(self):
        # Initialize the symbol table
        self.symbols = { }

    def visit_PrintStatement(self, node):
        self.visit(node.value)
        if node.value.type == '<deref>':
            node.value.type = 'char'

    def visit_ConstDeclaration(self, node):
        self.visit(node.value)
        node.type = node.value.type
        if node.name in self.symbols:
            error(node.lineno, f'{node.name} redefined. Previous definition on {self.symbols[node.name].lineno}')
        else:
            self.symbols[node.name] = node

    def visit_VarDeclaration(self, node):
        self.visit(node.datatype)
        node.type = node.datatype.type
        if node.value:
            self.visit(node.value)
            if node.value.type == '<deref>':
                node.value.type = node.type
            if node.value.type != node.type:
                error(node.lineno, f'type error. {node.type} = {node.value.type}')

        if node.name in self.symbols:
            error(node.lineno, f'{node.name} redefined. Previous definition on {self.symbols[node.name].lineno}')
        self.symbols[node.name] = node

    def visit_SimpleLocation(self, node):
        if node.name not in self.symbols:
            error(node.lineno, f'{node.name} undefined')
            node.type = None
            return 
        sym = self.symbols[node.name]
        if node.usage == 'write' and not isinstance(sym, VarDeclaration):
            error(node.lineno, f"Can't assign to {node.name}")
            node.type = None
        elif node.usage == 'read' and not isinstance(sym, (VarDeclaration,ConstDeclaration)):
            error(node.lineno, f"Can't read from {node.name}")
            node.type = None
        else:
            node.type = sym.type

    def visit_Assignment(self, node):
        node.location.usage = 'write'
        self.visit(node.location)
        self.visit(node.value)

        if node.value.type == '<deref>':
            node.value.type = node.location.type

        if node.location.type == '<deref>':
            node.location.type = node.value.type

        # Default to char (byte) if nothing known
        if node.location.type == '<deref>':
            node.location.type = 'char'
            node.value.type = 'char'

        if node.location.type != node.value.type:
            error(node.lineno, f'type error. {node.location.type} = {node.value.type}')

    def visit_ReadValue(self, node):
        node.location.usage = 'read'
        self.visit(node.location)
        node.type = node.location.type

    def visit_IntegerLiteral(self, node):
        node.type = lookup_type('int')

    def visit_FloatLiteral(self, node):
        node.type = lookup_type('float')

    def visit_CharLiteral(self, node):
        node.type = lookup_type('char')

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        # Adapt the type if dynamic
        if node.left.type == '<deref>':
            node.left.type = node.right.type
        if node.right.type == '<deref>':
            node.right.type = node.left.type
        node.type = check_binary_op(node.op, node.left.type, node.right.type)
        if not node.type:
            error(node.lineno, f'Unsupported binary op {node.left.type} {node.op} {node.right.type}')
            # Discussion: Even when there's a type error, you still have to
            # assign a resultant type to the node to make subsequent type checking
            # work (otherwise, you'll get AttributeError exceptions).  The
            # above assignment will leave the type set to None.  If you 
            # want it set to something else, you'll need to think about it.

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        node.type = check_unary_op(node.op, node.operand.type)
        if not node.type:
            error(node.lineno, f"Unsupported unary op {node.op}{node.operand.type}")

    def visit_TypeCast(self, node):
        self.visit(node.value)
        node.type = lookup_type(node.name)
        if node.value.type == '<deref>':
            node.value.type = node.type

    def visit_SimpleType(self, node):
        node.type = lookup_type(node.name)
        if not node.type:
            error(node.lineno, f'unknown type name {node.name}')

    def visit_GrowMemory(self, node):
        self.visit(node.incr)
        if node.incr.type != 'int':
            error(node.lineno, f'Memory increment must be an integer')
            node.type = None
        else:
            node.type = node.incr.type

    def visit_MemoryLocation(self, node):
        self.visit(node.addr)
        if node.addr.type != 'int':
            error(node.lineno, f'Memory address must be an integer')
            node.type = None
        else:
            node.type = '<deref>'

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)

def main():
    '''
    Main program. Used for testing
    '''
    import sys
    from .parser import parse

    if len(sys.argv) < 2:
        sys.stderr.write('Usage: python3 -m wabbit.checker filename\n')
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)
    if '--show-types' in sys.argv:
        for depth, node in flatten(ast):
            print('%s: %s%s type: %s' % (getattr(node, 'lineno', None), ' '*(4*depth), node,
                                         getattr(node, 'type', '(not set)')))

if __name__ == '__main__':
    main()



