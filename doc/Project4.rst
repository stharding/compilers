Project 4 - Code Generation
---------------------------

Added files::
 
    wabbit/ircode.py

Preliminaries
~~~~~~~~~~~~~

Don't forget to commit and tag your Project 3 code::

     bash % git commit -m "Project 3 complete"
     bash % git tag project3

Overview
~~~~~~~~

In this part of the project, you are going to make your compiler
generate intermediate instruction code in the form of simple static
machine. The output of your compiler will be a sequence of tuples that
look a lot like an abstract machine code.  This code is going to be
the basis for creating different kinds of compiler backends.  Further
instructions are found in the file ``wabbit/ircode.py``.

Testing
~~~~~~~

There are a series of test files::

    Tests/irtest0.wb
    Tests/irtest1.wb
    Tests/irtest2.wb
    Tests/irtest3.wb
    Tests/irtest4.wb

To run these tests, use a command such as::

    bash % python3 -m wabbit.ircode Tests/irtest0.wb

Each test file contains some implementation hints and expected output.
When you're done, you can also try your compiler on the following files::

    Tests/inttest.wb
    Tests/floattest.wb
    Tests/chartest.wb

These tests run the compiler through all of the basic operations on
the different datatypes.



