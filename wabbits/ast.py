# ast.py
'''
Abstract Syntax Tree (AST) objects.
-----------------------------------

This file defines classes for different kinds of nodes of an Abstract
Syntax Tree.  During parsing, you will create these nodes and connect
them together.  In general, you will have a different AST node for
each kind of grammar rule.  A few sample AST nodes can be found at the
top of this file.  You will need to add more on your own.

This file has a small bit of metaprogramming to simplify specification
and to perform some validation steps.  Do not modify the first part. 
'''

# DO NOT MODIFY
# -------------
class AST(object):
    _nodes = { } 

    @classmethod
    def __init_subclass__(cls):
        AST._nodes[cls.__name__] = cls

        if not hasattr(cls, '__annotations__'):
            return

        cls._fields = list(cls.__annotations__)

    def __init__(self, *args, **kwargs):
        if len(args) != len(self._fields):
            raise TypeError(f'Expected {len(fields)} arguments')
        for name, val in zip(self._fields, args):
            setattr(self, name, val)
            
        for name, val in kwargs.items():
            setattr(self, name, val)

    def __repr__(self):
        parts = []
        for name in self._fields:
            val = getattr(self, name)
            if isinstance(val, AST):
                parts.append(f'{name}={type(val).__name__}')
            elif isinstance(val, list):
                parts.append(f'{name}=[ len={len(val)} ]')
            else:
                parts.append(repr(val))
        argstr = ', '.join(parts)
        return f'{type(self).__name__}({argstr})'

# ----------------------------------------------------------------------
# Specific AST nodes.
#
# For each of these nodes, you need to add type annotations that
# specify which fields are to be stored.  Just as an example, for a
# binary operator, you might store the operator, the left expression,
# and the right expression like this:
#
#    class Expression(AST):
#          pass
#
#    class BinOp(AST):
#          op : str
#          left : Expression
#          right : Expression
#
# The "types" on the right are merely suggestions and don't have 
# any effect on the underlying operation.
#
# In the parser.py file, you're going to create nodes using code
# similar to this:
#
#    class WabbitParser(Parser):
#        ...
#        @_('expr PLUS expr')
#        def expr(self, p):
#            return BinOp(p[1], p.expr0, p.expr1)
#
# ----------------------------------------------------------------------

# Abstract AST nodes.  These are not instantiated directly, but other
# classes inherit from them.

class Statement(AST):
    '''
    Base class for all statements
    '''

class DataType(AST):
    '''
    Base class for a datatype
    '''

class Location(AST):
    '''
    Base class for locations
    '''

class Expression(AST):
    '''
    Base class for all expressions
    '''

# Concrete AST nodes.  These are instantiated in the parser

class SimpleType(DataType):
    '''
    A simple datatype name (e.g., 'int', 'float')
    '''
    name : str


class SimpleLocation(Location):
    '''
    A simple location as a name
    '''
    name : str


class MemoryLocation(Location):
    '''
    A memory location as `addr
    '''
    addr : Expression


class PrintStatement(Statement):
    '''
    print value ;
    '''
    value : Expression

class ConstDeclaration(Statement):
    '''
    const name = value ;
    '''
    name  : str
    value : Expression


class VarDeclaration(Statement):
    '''
    var name datatype [ = value ];
    '''
    name     : str
    datatype : DataType
    value    : (Expression, type(None))


class Assignment(Statement):
    '''
    location = value ;
    '''
    location : Location
    value : Expression


class Literal(Expression):
    '''
    Base class for a literal value such as 2, 2.5, or "two"
    '''

class IntegerLiteral(Literal):
    value : int


class FloatLiteral(Literal):
    value : float


class CharLiteral(Literal):
    value : str


class BinOp(Expression):
    '''
    A Binary operator such as 2 + 3 or x * y
    '''
    op    : str
    left  : Expression
    right : Expression


class UnaryOp(Expression):
    '''
    A Unary operator such as -x or +x
    '''
    op      : str
    operand : Expression


class ReadValue(Expression):
    '''
    The value of a location
    '''
    location : Location

    @property 
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value
        self.location.type = value


class TypeCast(Expression):
    '''
    typename(value)
    '''
    name : str
    value : Expression


class GrowMemory(Expression):
    '''
    Grow memory.  ^incr
    '''
    incr : Expression

# ----------------------------------------------------------------------
#                  DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

# The following classes for visiting and rewriting the AST are taken
# from Python's ast module.   It's really easy to make mistakes when
# naming methods in visitor classes so there's a bit of metaprogramming
# to make sure you're not writing duplicate definitions and to make
# sure your methods match up with the names of actual AST nodes.

# DO NOT MODIFY
class VisitDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise AttributeError(f'Duplicate definition for {key}')
        super().__setitem__(key, value)
        

class NodeVisitMeta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        return VisitDict()


class NodeVisitor(metaclass=NodeVisitMeta):
    '''
    Class for visiting nodes of the parse tree.  This is modeled after
    a similar class in the standard library ast.NodeVisitor.  For each
    node, the visit(node) method calls a method visit_NodeName(node)
    which should be implemented in subclasses.  The generic_visit() method
    is called for all nodes where there is no matching visit_NodeName() method.

    Here is a example of a visitor that examines binary operators:

        class VisitOps(NodeVisitor):
            visit_BinOp(self,node):
                print('Binary operator', node.op)
                self.visit(node.left)
                self.visit(node.right)
            visit_UnaryOp(self,node):
                print('Unary operator', node.op)
                self.visit(node.expr)

        tree = parse(txt)
        VisitOps().visit(tree)
    '''
    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if isinstance(node, list):
            for item in node:
                self.visit(item)
        elif isinstance(node, AST):
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            visitor(node)
    
    def generic_visit(self,node):
        '''
        Method executed if no applicable visit_ method can be found.
        This examines the node to see if it has _fields, is a list,
        or can be further traversed.
        '''
        for field in getattr(node, '_fields'):
            value = getattr(node, field, None)
            self.visit(value)

    @classmethod
    def __init_subclass__(cls):
        '''
        Sanity check. Make sure that visitor classes use the right names
        '''
        for key in vars(cls):
            if key.startswith('visit_'):
                assert key[6:] in AST._nodes, f"{key} doesn't match any AST node"

# DO NOT MODIFY
def flatten(top):
    '''
    Flatten the entire parse tree into a list for the purposes of
    debugging and testing.  This returns a list of tuples of the
    form (depth, node) where depth is an integer representing the
    parse tree depth and node is the associated AST node.
    '''
    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []
        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes
