Exercise 6 - Relations and Booleans
-----------------------------------

This exercise is just an overview of concepts.  Very little
programming is involved.  Just read and work a few examples.

Basic Relations
~~~~~~~~~~~~~~~

Programming languages have operations for relations.  For example::

     a < b
     a <= b
     a > b
     a >= b
     a == b
     a != b

Relations are different than many other binary operators in that the
result type is a boolean, not the same as the operands.  For example::

    >>> a = 2
    >>> b = 3
    >>> a < b
    True
    >>> a > b
    False
    >>>

For booleans, there are additional logical operations for ``and``,
``or``, and ``not``::

    >>> a < b and a > 0
    True
    >>> a > b or a < 0
    False
    >>> not a < b
    False
    >>>

Precedence Rules
~~~~~~~~~~~~~~~~

Relations have lower precedence than other math operators.  For example::

    >>> 1 + 4 < 3 + 5
    True
    >>>
    
Evaluates as::

    >>> (1 + 4) < (3 + 5)
    True
    >>>

Boolean operators ``and`` and ``or`` have lower precedence than relations::

    >>> 2 < 3 and 0 < 1
    True
    >>>

Evaluates as::

    >>> (2 < 3) and (0 < 1)
    True
    >>>

Python allows comparison operators to be chained together::

    >>> 2 < 3 < 0
    False
    >>> 2 < 3 > 0
    True
    >>> 2 < 3 > 0 < 10 > -1
    True
    >>>

Chaining is the same as this::

    >>> 2 < 3 and 3 < 0
    False
    >>> 2 < 3 and 3 > 0
    True
    >>> 2 < 3 and 3 > 0 and 0 < 10 and 10 > -1
    True

Syntactically, it's a little weird to write things such as ``x < y > z``.  
In fact, most programming languages don't permit it.  So, this
is something you might want to disallow in your programming language.
That is, the relations can only be used to compare two values.

Short-circuit Evaluation
~~~~~~~~~~~~~~~~~~~~~~~~

One thing you might ponder is whether or not you support short-circuit
evaluation of booleans operators ``and`` and ``or``.  In most languages,
evaluation stops once the final result can be determined.  Here's an
example that illustrates::

    >>> x = 10
    >>> (x != 0) or (x / 0)
    True
    >>>

Notice how the division by zero did not take place. Since the first
operand was ``True``, there's no need to evaluate the second operand.

You do NOT need to implement short-circuit evaluation in your compiler,
but think about it.  If you think you can add it, do it.



