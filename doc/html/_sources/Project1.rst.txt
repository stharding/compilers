Project 1 - Lexing
------------------

Files Modified::

    wabbit/errors.py
    wabbit/tokenizer.py

Preliminaries
~~~~~~~~~~~~~

All of your work on the compiler is going to take place in a directory
``wabbit``.  In that directory, you will already find a set of files
corresponding to different parts of the compiler project.  Each 
file has further directions about how to proceed. 

It is strongly advised that you put your work under version control
using what tool you're comfortable using.  For example with Git::

    bash % cd compilers
    bash % git init
    bash % git add wabbit/*
    bash % git commit -m "Project start" .
    bash %

For the remainder of the project, it is strongly advised that you work
with all files under version control and commit changes after every
major project stage.  Should you break something in a later project,
this will make it easier to go back.

Your Task
~~~~~~~~~

The first part of the compilers project involving a lexer for a subset
of the Wabbit language involving expressions.  Go to the file
``tokenizer.py`` and follow the instructions contained within.

Testing
~~~~~~~

The following files can be used for testing the input to your lexer::

     Tests/lextest0.wb
     Tests/lextest1.wb
     Tests/lextest2.wb
     Tests/lextest3.wb
     Tests/lextest4.wb
     Tests/lextest5.wb

You should run the tests by typing::

     bash % python3 -m wabbit.tokenizer filename
     ... get output ...
     bash %

If you need to compare your output against the reference compiler,
use::

    bash % python3 -m wabbits.tokenizer filename


