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

    # For a declaration, you'll need to check that it isn't already defined.
    # You'll put the declaration into the symbol table so that it can be looked up later
    def visit_ConstDeclaration(self, node):
        self.visit(node.value)
        if node.name in self.symbols:
            print(
                f"Error: Line {node.lineno}, '{node.name}' "
                f"previousely defined here: Line {self.symbols[node.name].lineno}"
            )
        self.symbols[node.name] = node
        node.datatype = node.type = node.value.type
        node.constant = True
        node.value.constant = True

    def visit_VarDeclaration(self, node):
        if node.value:
            self.visit(node.value)
        if node.name in self.symbols:
            print(
                f"Error: Line {node.lineno}, '{node.name}' "
                f"previousely defined here: Line {self.symbols[node.name].lineno}"
            )

        if not lookup_type(node.datatype):
            print(f"Error: Line {node.lineno}, unknown type {node.datatype}.")
        elif node.value and node.value.type == 'memloc':
            pass
        elif node.value and node.datatype != node.value.type:
            print(f"Error: Line {node.lineno}, type mismatch in var "
                  f"declaration: declared type '{node.datatype}' "
                  f"initialized with value of type '{node.value.type}'.")
        self.symbols[node.name] = node
        node.constant = False
        if node.value:
            node.value.constant = False
        node.type = node.datatype

    # A location represents a place where you can read/write a value.
    # You'll need to consult the symbol table to find out information about it
    def visit_SimpleLocation(self, node):
        if node.name in self.symbols:
            node.type = self.symbols[node.name].datatype
        else:
            print(f"Error: Line {node.lineno}, Name error. '{node.name}' not declared")
            node.type = None

        if node.name in self.symbols:
            node.constant = getattr(self.symbols[node.name], 'constant', False)
        else:
            print(f'Error: Line {node.lineno}, undeclared variable {node.name}.')

    def visit_LoadValue(self, node):
        self.visit(node.location)
        node.type = node.location.type
        node.location.usage = 'load'

    # For literals, you'll need to assign a type to the node and allow it to
    # propagate.  This type will work it's way through various operators
    def visit_IntegerLiteral(self, node):
        node.type = lookup_type("int")

    def visit_FloatLiteral(self, node):
        node.type = lookup_type("float")

    def visit_CharLiteral(self, node):
        node.type = lookup_type("char")

    # For operators, you need to visit each operand separately.  You'll
    # then need to make sure the types and operator are all compatible.
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        # Perform various checks here
        binop_type = check_binary_op(
            node.op, node.left.type, node.right.type
        )
        if node.left.type == 'memloc' and node.right.type != 'memloc':
            binop_type = node.right.type
        elif node.left.type == 'memloc' and node.right.type != 'memloc':
            binop_type = node.left.type

        if not binop_type:
            if (hasattr(node.left, 'error') or
                hasattr(node.right, 'error')
            ):
                node.type = None
                node.error = True
                return

            print(f'Error: Line {node.lineno}. '
                  f'Invalid types: {node.left.type}, {node.right.type} '
                  f"for operator: '{node.op}' in expression.")
            node.error = True
        node.type = binop_type

    def visit_UnaryOp(self, node):
        self.visit(node.value)

        unary_type = check_unary_op(node.op, node.value.type)
        if not unary_type:
            print(f'Error: Line {node.lineno}, invalid unary operation '
                  f"'{node.op}' for type '{node.value.type}' "
                  f"in expression {node.op}{node.value.value}")
            node.error = True
        node.type = unary_type

    def visit_SimpleType(self, node):
        # Associate a type name such as "int" with a Type object
        node.type = node.name

    def visit_Assignment(self, node):
        self.visit(node.value)
        self.visit(node.location)
        node.location.usage = 'store'

        if hasattr(node, 'name'):
            if self.symbols[node.name].constant:
                print(f"Error: Line: {node.lineno}, '{node.location}' is a constant.")

        if node.value.type == 'memloc':
            pass
        elif node.location.type == 'memloc':
            pass
        elif node.location.type != node.value.type:
            print(
                f"Error: Line {node.lineno}, type mismatch in assignment for "
                f"variable of type {node.location.type} for value of type {node.value.type}."
            )
        node.type = None

    def visit_PrintStatement(self, node):
        node.type = 'void'
        self.visit(node.value)

    def visit_TypeCast(self, node):
        self.visit(node.value)
        node.type = node.name

    def visit_MemoryLocation(self, node):
        self.visit(node.value)
        node.type = 'memloc'

    def visit_GrowMemory(self, node):
        self.visit(node.value)
        node.type = 'int'

    # You'll need to add more visit_* methods here


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
