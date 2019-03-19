# typesys.py
'''
Type System
===========
This file implements basic features of the type system.  There is a
lot of flexibility possible here, but the best strategy might be to
not overthink the problem.  At least not at first.  Here are the
minimal basic requirements:

1. Types have identity (e.g., minimally a name such as 'int', 'float', 'char')
2. Types have to be comparable. (e.g., int != float).
3. Types support different operators (e.g., +, -, *, /, etc.)

One way to achieve all of these goals is to start off with
some kind of table-driven approach.  It's not the most 
sophisticated thing, but it will work as a starting point.
You can come back and refactor the type system later.
'''
# Set of valid typenames
typenames = { 'int', 'float', 'char' }

# Table of all supported binary operations and result types
_binary_ops = {
    # Integer operations
    ('+', 'int', 'int') : 'int',
    ('-', 'int', 'int') : 'int',
    ('*', 'int', 'int') : 'int',
    ('/', 'int', 'int') : 'int',
    
    # Float operations
    ('+', 'float', 'float') : 'float',
    ('-', 'float', 'float') : 'float',
    ('*', 'float', 'float') : 'float',
    ('/', 'float', 'float') : 'float',

    # Character operations
}

_unary_ops = {
    # Integer operations
    ('+', 'int') : 'int',
    ('-', 'int') : 'int',

    # Float operations
    ('+', 'float') : 'float',
    ('-', 'float') : 'float',
}

def lookup_type(name):
    # Given the name of a primitive type, this looks up the
    # appropriate "type" object here.  For starting out, types are
    # just names, but later on they could be more advanced objects.
    if name in typenames:
        return name
    else:
        return None

def check_binary_op(op, left, right):
    # Check if a binary operation is allowed or not.  Returns the
    # result type or None if not supported.
    return _binary_ops.get((op, left, right))

def check_unary_op(op, expr):
    # Check if a unary operation is allowed or not. Returns the result
    # type or None if not supported.
    return _unary_ops.get((op, expr))

    





          




