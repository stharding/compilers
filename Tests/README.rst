Testing Guide
=============

Project1:  Lexing
-----------------
python3 -m wabbit.tokenizer Tests/testlex0.wb       # Tests simple tokens
python3 -m wabbit.tokenizer Tests/testlex1.wb       # Tests identifiers
python3 -m wabbit.tokenizer Tests/testlex2.wb       # Tests numbers
python3 -m wabbit.tokenizer Tests/testlex3.wb       # Tests character literals
python3 -m wabbit.tokenizer Tests/testlex4.wb       # Tests everything
python3 -m wabbit.tokenizer Tests/testlex5.wb       # Tests bad input


Project2: Parsing
-----------------
There are a series of tests that progressively build up more and more
advanced parts of the language. Work them in order.  Each test file
has a description of what is required along with some hints::

python3 -m wabbit.parser Tests/parsetest0.wb      
python3 -m wabbit.parser Tests/parsetest1.wb
python3 -m wabbit.parser Tests/parsetest2.wb
python3 -m wabbit.parser Tests/parsetest3.wb
python3 -m wabbit.parser Tests/parsetest4.wb
python3 -m wabbit.parser Tests/parsetest5.wb
python3 -m wabbit.parser Tests/parsetest6.wb
python3 -m wabbit.parser Tests/parsetest7.wb

Project 3: Type Checking
------------------------
This part of the project focuses on adding error checks and
validation to your compiler.  It's potentially quite tricky.
Work through each test methodically. Details are given in each
test file::

python3 -m wabbit.checker Tests/checktest0.wb
python3 -m wabbit.checker Tests/checktest1.wb
python3 -m wabbit.checker Tests/checktest2.wb
python3 -m wabbit.checker Tests/checktest3.wb
python3 -m wabbit.checker Tests/checktest4.wb
python3 -m wabbit.checker Tests/checktest5.wb
python3 -m wabbit.checker Tests/checktest6.wb
python3 -m wabbit.checker Tests/checktest7.wb

In order to proceed to Project 4, you don't need to check every
possible error, but it is critical that your type checking code
properly propagate datatypes.

Project 4: Intermediate Code
----------------------------
Try running the following tests to test basic code generation.
For each of these tests, you will need to visually compare
expected output with the output of your compiler.  Each test
file has a sample of the output:

python3 -m wabbit.ircode Tests/irtest0.wb
python3 -m wabbit.ircode Tests/irtest1.wb
python3 -m wabbit.ircode Tests/irtest2.wb
python3 -m wabbit.ircode Tests/irtest3.wb
python3 -m wabbit.ircode Tests/irtest4.wb
python3 -m wabbit.ircode Tests/irtest5.wb

Project 5: Code Generation
--------------------------
The same tests as Project 4 should run.

python3 -m wabbit.wasm Tests/irtest0.wb
python3 -m wabbit.wasm Tests/irtest1.wb
python3 -m wabbit.wasm Tests/irtest2.wb
python3 -m wabbit.wasm Tests/irtest3.wb
python3 -m wabbit.wasm Tests/irtest4.wb
python3 -m wabbit.wasm Tests/irtest5.wb

In addition, there are these two basic tests of integers and floats

python3 -m wabbit.wasm Tests/inttest.wb
python3 -m wabbit.wasm Tests/floattest.wb

If you implement other parts of the project such as the interpreter,
transpiler, or LLVM generator, they should all work with these
tests.  For example:

python3 -m wabbit.llvmgen Tests/inttest.wb
python3 -m wabbit.compile Tests/inttest.wb
python3 -m wabbit.interp Tests/inttest.wb
python3 -m wabbit.python Tests/inttest.wb
python3 -m wabbit.run Tests/inttest.wb

Project 6 : Comparisons and Boolean Operators
---------------------------------------------
Run the following tests on comparison operators::

python3 -m wabbit.wasm Tests/testrel_int.wb
python3 -m wabbit.wasm Tests/testrel_float.wb
python3 -m wabbit.wasm Tests/testrel_char.wb

Note: You might need to run other kinds of more preliminary tests
during development.

The following tests checks some bad comparisons:

python3 -m wabbit.wasm Tests/testrel_bad.wb

Project 7: Control Flow
-----------------------
The following test files involve control flow features::

python3 -m wabbit.wasm Tests/cond.wb
python3 -m wabbit.wasm Tests/nestedcond.wb
python3 -m wabbit.wasm Tests/fact.wb
python3 -m wabbit.wasm Tests/fib.wb
python3 -m wabbit.wasm Tests/nestedwhile.wb

This tests some bad control flow::

python3 -m wabbit.wasm Tests/badcontrol.wb

Project 8: Functions
--------------------

python3 -m wabbit.wasm Tests/func.wb
python3 -m wabbit.wasm Tests/funcret.wb    # Errors involving return statements
python3 -m wabbit.wasm Tests/funcerrors.wb # Various function related errors
python3 -m wabbit.wasm Tests/mandel.wb     # Mandelbrot set

For project 8, you can also start running code in the Programs/ directoy.

