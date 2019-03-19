Project 7 - Control Flow
------------------------

Files Modified::

   Everything

Caution
~~~~~~~

Make sure you fully work through Exericse 7 before starting this
project.

Preliminaries
~~~~~~~~~~~~~

Don't forget to commit and tag your Project 6 code::

     bash % git commit -m "Project 6 complete"
     bash % git tag project6

Once again, this project involves changes to almost every part of the
compiler.   Failure to commit your previous code is not advised.

Overview
~~~~~~~~

In this project, you're going to add basic control-flow constructs to
your compiler.  Specifically, an ``if-else`` statement::

    if relation {
         statements
    } else {
         statements
    }

and a ``while``-loop::

    while relation {
        statements
    }

These statements are to have the familiar semantics you are used to
from other programming languages.

Suggested sequence of work:

1. Add tokens for ``if``, ``else``, and ``while`` to ``wabbit/tokenizer.py``.

2. Add new AST nodes for a conditional and while-loop to ``wabbit/ast.py``.

3. Add new parsing rules to ``wabbit/parser.py``.

4. Add new type-checking code to ``wabbit/checker.py``.  Your checking code 
   should enforce the requirement that the expression given to ``if`` or ``while``
   evaluates to a boolean value.

5. Modify the file ``wabbit/ircode.py`` to generate code using structured
   control flow.  See the details below about this:

6. Modify the files ``wabbit/llvmgen.py``, ``wabbit/wasm.py``, and ``wabbit/python.py``
   So that they emit code with control flow.

Making all of these changes will take some time, but may not involve
as many changes to compiler as you think.  The most tricky parts will
involve changes to mapping structure assembly to LLVM.  Again, keep reading
for more information.

Structured Control Flow
~~~~~~~~~~~~~~~~~~~~~~~

In generating intermediate code, we're going to rely on "structured
control flow."  What is structured control flow you ask?  It's basically
the same programming technique you use now!  For example, an if-statement
in Python::

    if a < b:
        minval = a
    else:
        maxval = b

Or a while-loop::

    while n > 0:
        print(n)
        n = n - 1

Notice the lack of "goto" statements.  At the assembly level, we're going
to introduce a few new instructions::

    ('IF',)
    ... consequent ...
    ('ELSE',)
    ... alternative ...
    ('ENDIF',)

The 'IF' instruction takes the top element of the stack and uses it
to take one of two code branches.   

For loops, you're going to use `LOOP`, `CBREAK`, and `ENDLOOP` like this::

    ('LOOP',)
    ... evaluate loop test ...
    ('CBREAK',)            # Go to instruction after ENDLOOP
    ... loop body ...
    ('ENDLOOP,)            # Jump back to top of loop


For the above Python examples, here's what the low-level IR code might 
look like::

    # Example of if-statement
    ('LOADI', 'a')
    ('LOADI', 'b')
    ('LTI',)
    ('IF',)
    ('LOADI', 'a')
    ('STOREI', 'minval')
    ('ELSE',)
    ('LOADI', 'b'))
    ('STOREI', 'minval')
    ('ENDIF',)

    # Example of while-loop
    ('LOOP',)
    ('LOADI', 'n')
    ('CONSTI', 0)
    ('LEI',)          # Note: Test is inverted (true breaks out)
    ('CBREAK',)         
    ('LOADI', 'n')
    ('PRINTI',)
    ('LOADI', 'n')
    ('CONSTI', 1)
    ('SUBI',)
    ('STOREI', 'n')
    ('ENDLOOP',)

Structured control-flow very closely follows the control flow model
of the original Wabbit source code.  Generating the above code
should be fairly straightforward--mainly you need to place the various
IF, ELSE, ENDIF, LOOP, and ENDLOOP instructions in the right place
when emitting instructions.

Structured control-flow does not rely on goto statements or labels.
Thus, if you've written low-level machine language before, it's going
to look a little weird.

Wasm Code Generation
~~~~~~~~~~~~~~~~~~~~
Generating Wasm code for structured control flow is 
straightforward because Wasm itself uses structured control flow.  The
``IF``, ``ELSE``, and ``ENDIF`` instructions should translate almost
directly to the Wasm `if` instruction.

Loops in Wasm are going to be slightly more tricky.  For this, you
need to enclose the loop both in an outer block and by an inner loop
instruction.  In pseudocode, it looks like this::

    block {
      loop {
          # Evaluate the loop test
          ...
          br_if 1     # Break to enclosing block if eval stack is true
          # Evaluate the loop body
          ...
          br 0        # Go back to top of loop
      }
      # The br_if 1 targets this position
      ...
    }

All of these elements (``block``, ``loop``, ``br_if``, and ``br``) are
Wasm instructions.  See pg. 90 of the WebAssembly Specification, v1.0 
for the precise encoding.

Generating LLVM
~~~~~~~~~~~~~~~

One challenge will involve translating structured control to LLVM's
block structure.  To do this, you should create a series of
basic blocks immediately upon encountering the ``IF`` instruction.
For example, something like this::

     def emit_IF(self):
         then_block = self.function.append_basic_block()
         else_block = self.function.append_basic_block()
         cont_block = self.function.append_basic_block()
         self.builder.cbranch(self.pop(), then_block, else_block)
	 self.builder.position_at_end(then_block)
	 self.block_stack.append((then_block, else_block, cont_block))

You'll need to save these blocks on some kind of stack for later. 
In the ``ELSE`` instruction, you'll refer back to the block stack like
this::

     def emit_ELSE(self):
         self.builder.branch(self.block_stack[-1][2])           # cont_block
         self.builder.position_at_end(self.block_stack[-1][1])  # else_block

Finally, in the ``ENDIF`` instruction, you'll pop the stack::

     def emit_ENDIF(self):
         self.builder.branch(self.block_stack[-1][2])
         self.builder.position_at_end(self.block_stack[-1][2])
         self.block_stack.pop()

It is critical that every LLVM block be terminated by a branch. So,
when generating code, you need to make sure approach branch
instructions are generated to get control flow to jump.  If you forget
this, you'll get crazy error messages. You'll also get an error if you
attempt to put more than one branch in the same block or if you put
instructions after a branch.

Generating the ``LOOP`` code is similar to ``IF``. Create the basic 
blocks when you see the ``LOOP`` instruction and save them on a stack
for later use in ``CBREAK`` and ``ENDLOOP`` instructions.

Testing
~~~~~~~

The following files are available for testing::

    Tests/cond.wb          # A simple conditional
    Tests/nestedcond.wb    # Nested conditionals
    Tests/fact.wb          # Compute factorials
    Tests/fib.wb           # Compute fibonacci numbers
    Tests/nestedwhile.wb   # Nested while loops
    Tests/badcontrol.wb    # Some error checks
    Tests/mandel_loop.wb   # See a mandelbrot set

To run the tests, you should just be able to run your compiler using
your favorite output mode. For example::

    bash % python3 -m wabbit.run Tests/fact.wb
    1
    2
    6
    24
    120
    720
    5040
    40320
    362880
    bash %





