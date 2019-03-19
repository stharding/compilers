Exercise 7 - Basic Blocks and Control Flow
------------------------------------------

A sequence of simple operations where there is a single entry and
exit point with no changes in control flow is known as a basic block.
For example::

       # Example of a basic block
       a = 2
       b = 3
       c = a + b

Programs tend to consist of many basic blocks joined together
by various control-flow statements such as conditions and loops.
For example::

       a = 2
       b = 3
       if a < b:
            c = a + b
       else:
            c = a - b
       print(c)

In this code, there are four basic blocks::

      b1:    a = 2
             b = 3
             a < b

      b2:    c = a + b

      b3:    c = a - b

      b4:    print(c)

The condition causes the code to branch to either block b2 or block b3.  
One way to view this is as a control-flow graph::

                 |--------------|
                 |  b1:  a = 2  |
                 |       b = 3  |
                 |       a < b  |
                 |--------------|
               /                 \
              / True         False\
             /                     \
    |------------------|       |-----------------|
    |  b2:  c = a + b  |       |  b3: c = a - b  |
    |------------------|       |-----------------|
                 \              /
                  \            /
                  |--------------|
                  | b4: print(c) |
                  |--------------|

The nodes of the graph represent basic blocks--which are just simple
instruction sequences.  Edges of the graph represent jumps to to a
different basic block.  Sometimes an edge depends on the result
of a condition or relation.   An edge might also be an unconditional
jump.

Internally, a compiler might construct a control flow graph in order
to further analyze the structure of the program (e.g., detecting when
variables are no longer needed, finding dead code, performing certain
optimizations, etc.).

Expressing Control Flow with Jump Instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When generating code, there are different ways to express the
control flow graph.  One approach is to serialize the instruction
stream and to insert explicit jump instructions that link the blocks.
For example, like this::

                 |--------------|
                 |  b1:  a = 2  |
                 |       b = 3  |
                 |       a < b  |
                 |--------------|
                 | JMP_FALSE b3 |
                 |--------------|
                 | b2: c = a +b |
                 |--------------|
                 | JMP b4       |
                 |--------------|
                 | b3: c = a-b  |
                 |--------------|
                 | b4: print(c) |
                 |--------------|

This is how Python generates control-flow for its low-level instructions.
Take a look at this::

     >>> def foo(a,b):					   
             if a < b:					   
                     print("yes")				   
             else:						   
                     print("no")				   
      							   
     >>> import dis						   
     >>> dis.dis(foo)					   
       2           0 LOAD_FAST                0 (a) 		   
                   3 LOAD_FAST                1 (b) 		   
                   6 COMPARE_OP               0 (<) 		   
                   9 POP_JUMP_IF_FALSE       25 		   
     							   
       3          12 LOAD_GLOBAL              0 (print) 	   
                  15 LOAD_CONST               1 ('yes') 	   
                  18 CALL_FUNCTION            1 		   
                  21 POP_TOP              			   
                  22 JUMP_FORWARD            10 (to 35) 	   
     							   
       5     >>   25 LOAD_GLOBAL              0 (print) 	   
                  28 LOAD_CONST               2 ('no') 	   
                  31 CALL_FUNCTION            1 		   
                  34 POP_TOP              			   
             >>   35 LOAD_CONST               0 (None) 	   
                  38 RETURN_VALUE                               
     >>>

Carefully study the code.  Can you identify the basic blocks?
How does control flow of the if-statement pass from block to block?

Try disassembling a while-loop::

    >>> def countdown(n):					    
            while n > 0:					    
                print("T-minus",n)				    
                n -= 1					    
     							    
    >>> dis.dis(countdown)					    
      2           0 SETUP_LOOP              39 (to 42) 	    
            >>    3 LOAD_FAST                0 (n) 		    
                  6 LOAD_CONST               1 (0) 		    
                  9 COMPARE_OP               4 (>) 		    
                 12 POP_JUMP_IF_FALSE       41 		    
    							    
      3          15 LOAD_GLOBAL              0 (print) 	    
                 18 LOAD_CONST               2 ('T-minus') 	    
                 21 LOAD_FAST                0 (n) 		    
                 24 CALL_FUNCTION            2 		    
                 27 POP_TOP              			    
    							    
      4          28 LOAD_FAST                0 (n) 		    
                 31 LOAD_CONST               3 (1) 		    
                 34 INPLACE_SUBTRACT     			    
                 35 STORE_FAST               0 (n) 		    
                 38 JUMP_ABSOLUTE            3 		    
            >>   41 POP_BLOCK            			    
            >>   42 LOAD_CONST               0 (None) 	    
                 45 RETURN_VALUE         			    
    >>>                                                         

Again, study the disassembly.  Can you identify the basic blocks?
What is the control flow between blocks?  

Structured Control Flow
~~~~~~~~~~~~~~~~~~~~~~~

Instead of using jump instructions, an alternative approach is to use
what's known as structured control flow.  This is basically the
same approach as expressed in high-level languages like Python.
It's what you are doing by indenting blocks of code.

A conditional with structured-control flow might look like this::


                 |--------------|
                 |  a = 2       |
                 |  b = 3       |
                 |  a < b       |
                 |--------------|
                 | IF           |
                 |--------------|
                 | c = a +b     |
                 |--------------|
                 | ELSE         |
                 |--------------|
                 | c = a-b      |
                 |--------------|
                 | ENDIF        |
                 |--------------|
                 | print(c)     |
                 |--------------|

Notice, instead of emitting labels, you emit approach ``IF``, ``ELSE``, and
``ENDIF`` instructions to mark blocks.  

For looping constructs, structured control flow is often a bit counter-intuitive.
Suppose you have a while loop like this::

    while n > 0:
        print(n)
        n -= 1
    print("Done")

At a low level, it's easier to translate the code as if it were written like this::

    while True:
        if n > 0:
            break
        print(n)
        n -= 1
    print("Done")

The low-level instruction stream would look like this::


                 |--------------|
                 | LOOP         |
                 |--------------|
                 | not n > 0    |
                 |--------------|
                 | CBREAK       |   (Conditional Break)
                 |--------------|
                 | print(n)     |
                 | n -= 1       |
                 |--------------|
                 | ENDLOOP      |
                 |--------------|
                 | print("Done")|
                 |--------------|

The idea here is that the loop cycles endlessly until a conditional
break instruction makes it stop.  The placement of the ``CBREAK``
allows different kinds of looping constructs (e.g., do-while loops and
other variants).

Code Generation for Control Flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's see an example of how to generate intermediate code for
basic blocks and control flow.  Let's focus on this
small Python code sample::

     code = """\
     start
     if a < 0:
         a + b
     else:
         a - b
     done
     """

Compile the code and view the AST just to see what it looks like::
    
    >>> import ast
    >>> top = ast.parse(code)
    >>> print(ast.dump(top))
    Module(body=[Expr(value=Name(id='start', ctx=Load())),		     
    If(test=Compare(left=Name(id='a', ctx=Load()), ops=[Lt()],	     
    comparators=[Num(n=0)]), body=[Expr(value=BinOp(left=Name(id='a',    
    ctx=Load()), op=Add(), right=Name(id='b', ctx=Load())))],	     
    orelse=[Expr(value=BinOp(left=Name(id='a', ctx=Load()), op=Sub(),    
    right=Name(id='b', ctx=Load())))]), Expr(value=Name(id='done',	     
    ctx=Load()))])                                                       
    >>>

In Exercise 4, we took a look at how to walk the AST and turn it into
Python machine code.   We're just going to expand and adapt that code
by inserting block labels and jump instructions.

Take the code generator class from Exercise 4 and add a few new
features to it::

    import ast
    class CodeGenerator(ast.NodeVisitor):
        '''
        Sample code generator with basic blocks and control flow
        '''
        def __init__(self):
            self.code = []
            self._label = 0

        def new_block(self):
            self._label += 1
            return 'b%d' % self._label

        def visit_If(self,node):
            '''
            Example of compiling a simple Python if statement. 
            '''
            # Step 1: Evaluate the test condition
            self.visit(node.test)

            # Step 2: Make a block labels for both branches and the merge point
            ifblock = self.new_block()
            elseblock = self.new_block()
            mergeblock = self.new_block()

            self.code.append(('JUMP_IF_FALSE', elseblock))

            # Step 3: Traverse all of the statements in the if-body
            self.code.append(('BLOCK', ifblock))
            for bnode in node.body:
                self.visit(bnode)
            self.code.append(('JUMP', mergeblock))

            # Step 4: If there's an else-clause, create a new block and traverse statements
            if node.orelse:
                self.code.append(('BLOCK', elseblock))
                # Visit the body of the else-clause
                for bnode in node.orelse:
                    self.visit(bnode)

            # Step 5: Start a new block to continue on with more instructions
            self.code.append(('BLOCK', mergeblock))
        
        def visit_BinOp(self,node):
            self.visit(node.left)
            self.visit(node.right)
            opname = node.op.__class__.__name__
            inst = ("BINARY_"+opname.upper(),)
            self.code.append(inst)

        def visit_Compare(self,node):
            self.visit(node.left)
            opname = node.ops[0].__class__.__name__
            self.visit(node.comparators[0])
            inst = ("BINARY_"+opname.upper(),)
            self.code.append(inst)

        def visit_Name(self,node):
            if isinstance(node.ctx, ast.Load):
                inst = ('LOAD_GLOBAL',node.id)
            else:
                inst = ('Unimplemented,')
            self.code.append(inst)

        def visit_Num(self,node):
            inst = ('LOAD_CONST',node.n)
            self.code.append(inst)

When handling the ``if`` statement, the code generator makes new
block labels for the if-branch, the else-branch, and the merge
point.  It then follows each branch and emits instructions.  Block
labels are inserted as appropriate to indicate the start of each block.

Try running the following code fragment and studying the output::

    if __name__ == '__main__':			       
        top = ast.parse("""\			   
    start
    if a < 0:					   
       a + b					   
    else:						   
       a - b					   
    done						   
    """)						   
        gen = CodeGenerator()			   
        gen.visit(top)				   
        for instr in gen.code:
            print(instr)

You should see output that's pretty close to the Python disassembly like this::

    ('LOAD_GLOBAL', 'start')
    ('LOAD_GLOBAL', 'a')
    ('LOAD_CONST', 0)
    ('BINARY_LT',)
    ('JUMP_IF_FALSE', 'b2')
    ('BLOCK', 'b1')
    ('LOAD_GLOBAL', 'a')
    ('LOAD_GLOBAL', 'b')
    ('BINARY_ADD',)
    ('JUMP', 'b3')
    ('BLOCK', 'b2')
    ('LOAD_GLOBAL', 'a')
    ('LOAD_GLOBAL', 'b')
    ('BINARY_SUB',)
    ('BLOCK', 'b3')
    ('LOAD_GLOBAL', 'done')

Pay careful attention to block labels and jump instructions.

Your Task
~~~~~~~~~

Can you modify the ``blocks.py`` program to emit instructions
for structured-control flow instead?

Can you modify the ``blocks.py`` program so that it can work
with ``while`` loops?

