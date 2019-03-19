Project 5 - Code Generation
---------------------------

DO NOT START THIS PROJECT WITHOUT COMPLETING EXERCISE 5.

Files Modified::

     wabbit/interp.py
     wabbit/python.py
     wabbit/llvmgen.py
     wabbit/wasm.py

Possible modifications to::

     wabbit/run.py
     wabbit/compile.py
     wabbit/wabbitrt.c
     wabbit/Makefile

Preliminaries
~~~~~~~~~~~~~

Don't forget to commit and tag your Project 4 code::

     bash % git commit -m "Project 4 complete"
     bash % git tag project4

Overview
~~~~~~~~

In this project, you're actually going to make your compiler do
something.  This is a fairly big project wherein we're going to
create as many as 4 different compiler targets. 

In the first part, you're going to transpile Wabbit code to Python
source.  Go look at the file `wabbit/python.py` for further 
instructions.   The basic idea is that you'll be able to take 
a Wabbit code and turn it into a Python script of some kind.  Like
this::

    bash % python3 -m wabbit.python program.wb
    bash % python3 -m out.py
    ... look at output of program running ...

You should be able to run the same code used to test Project 4::

     Tests/irtest0.wb
     Tests/irtest1.wb
     Tests/irtest2.wb
     Tests/irtest3.wb
     Tests/irtest4.wb
     Tests/irtest5.wb

In the next step of the project, you're going to translate Wabbit 
to LLVM bitcode.  Go to the file `wabbit/llvmgen.py` and
follow the instructions inside. To see the LLVM output, you'll
type a command like this::

     bash % python3 -m wabbit.llvmgen Tests/irtest0.wb
     ... see LLVM output here ...

If you think it's working, build the Wabbit runtime support library::

     bash % cd wabbit
     bash % make 

Once you've done that, you might be able to actually run the code.
You can try a command like this::

     bash % python3 -m wabbit.compile Tests/irtest0.wb
     bash % ./a.out
     3
     3.5
     abash %

If compilation doesn't work (might be dicey on your machine), you can
alternatively try running the code using an LLVM JIT compiler::

     bash % python3 -m wabbit.run Tests/irtest0.wb
     3
     3.5
     bash %

Note: The ``compile.py`` and ``run.py`` programs might not require any 
modifications at all.  However, there are some platform dependencies so
some tweaking might be required.

The final output is Web Assembly.  Go to the file `wabbit/wasm.py` for
further instructions.   To generate Wasm, you'll use a command like this::

    bash % python3 -m wabbit.wasm Tests/irtest0.wb

To see your program run, you need to run a Python web server in the
same directory as the ``out.wasm`` file and point the browser at
http://localhost:8000/test.html.   Note: You can use ``python3 -m http.server`` 
to run a simple web server.

Testing
~~~~~~~

There are several tests in the ``Tests/`` directory that you can find.
For integer operations, you can try::

     bash % python3 -m wabbit.run Tests/inttest.wb
     6
     3
     -1
     12
     3
     1
     -1
     13
     bash %

For floats, try::

     bash % python3 -m wabbit.run Tests/floattest.wb
     6.000000
     3.000000
     -1.000000
     12.000000
     3.000000
     1.000000
     -1.000000
     13.000000
     bash %

For characters, try::

     bash % python3 -m wabbit.run Tests/chartest.wb
     hello
     world
     bash %

A Moment of Zen
---------------

Congratulations!  If you made it this far, you have the end-to-end
processing pipeline of the compiler implemented.  You can compile
basic statements and have them execute a few different environments.  

Take a few moments to contemplate what you've done, check your code
into version control, and then proceed onto Project 6.





     

