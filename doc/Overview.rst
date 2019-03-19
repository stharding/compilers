Compiler Project Overview
-------------------------

You are going to be implementing the core of a simple programming
language called "Wabbit."  Wabbit supports the following features:

- Evaluation of expressions (math)
- Integers, floats, characters, and bools.
- Assignment to variables
- Printing
- Basic control flow (if, while)
- User-defined functions

Although the language is simple, you are going to have to write all of
the core components of an actual compiler, including all of the
parsing, type checking, control-flow analysis, intermediate code
generation, and output code. 

The implementation approach is going to be incremental.  The first
five projects are going to take you through all of the core stages of
compilation of lexing, parsing, type checking, and code generation for
a small subset of the language.  The last three projects involve
expanding your compiler to include more advanced features.

Ultimately, the final output of your compiler will be Web Assembly,
LLVM, or transpiled Python.  These three targets will give you 
a rich flavor of what a compiler can do and how different things
work.

A Taste of Wabbit
~~~~~~~~~~~~~~~~~

Here is a sample of a simple Wabbit program that computes the ever-so-useful
Fibonacci numbers::

    /* fib.wb -  Compute fibonacci numbers */

    const LAST = 30;            // A constant declaration

    // A function declaration
    func fibonacci(n int) int {
         if n > 1 {              // Conditionals
            return fibonacci(n-1) + fibonacci(n-2);
         } else {
            return 1;
         }
     }

     func main() int {
         var n int = 0;           // Variable declaration
	 while n < LAST {         // Looping (while)
	    print fibonacci(n);   // Printing
            n = n + 1;            // Assignment
         }
	 return 0;
     }

The ``fib.wb`` program above can be found in the directory
``Programs/fib.wb``.

Running and Compiling Programs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ultimately the ``wabbit`` compiler will allow programs to be compiled
and executed in a variety of ways.  First, you'll be able to transpile
Wabbit source to a Python script.

    bash % python3 -m wabbit.python Programs/fib.wb
    bash % python3 out.py
    1
    1
    2
    3
    5
    8
    13
    21
    34
    55
    ...
    bash %

You should see output similar to the above being generated, albeit
very slowly.  This is the most portable technique for running Wabbit
code as it involves nothing but pure Python code.

The ``fib.wb`` program can also be compiled to a stand-alone executable::

    bash % python3 -m wabbit.compile Programs/fib.wb
    bash % ./a.out
    1
    1
    2
    3
    5
    ...
    bash %

This creates a program called ``a.out``.  If you run it, you should
see the same output as the Python code, but substantially faster. This
is executing native machine code on your system.  Creating this
executable requires the ``clang`` C/C++ compiler.  If you don't have
it installed correctly, compilation will probably fail.

If you don't have ``clang`` installed, you can also run the program as
a just-in-time compiled binary inside Python. To do this, you first need
to build a run-time library::

    bash % cd wabbit
    bash % make mac    #  Change to make linux on Linux

Next, you can try running the program::

    bash % cd ..
    bash % python3 -m wabbit.run Programs/fib.wb
    1
    1
    2
    3
    5
    ...
    bash %

Both the `compile` and `run` options use LLVM to generate native
machine code.

The final target for Wabbit is Web Assembly.  You can create a `.wasm`
file as follows:

    bash % python3 -m wabbit.wasm Programs/fib.wb

This creates a file `out.wasm`.   To run this program in the browser,
launch a web server:

    bash % python3 -m http.server

Next, got to your browser and load http://localhost:8000/test.html.
You should see the output the program appearing on a web page.
Refer to the file `test.html` to see how it's done.

Reference Implementation
~~~~~~~~~~~~~~~~~~~~~~~~

The ``wabbts`` directory contains a reference implementation for the
first part of the project that you can use for testing, hints, and
comparing against your own code.  It's okay to look at this code as
you work, but to get the most out of the project, you should work to
make your own solution.

As an aside, the reference implementation is a bare-bones implementation.
You should think of various ways to make your compiler and more featureful.

Language Reference
~~~~~~~~~~~~~~~~~~

The ``Wabbit.rst`` file contains an official specification for the language.

Playground
~~~~~~~~~~

The ``SillyWabbit/`` directory contains a full implementation of the language
interpreter in a form where you can experiment with Wabbit programs and see
what they do.  See the README file in that directory for more information.


