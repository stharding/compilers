Project 8 - Functions
---------------------

Files Modified::

     Everything!

Preliminaries
~~~~~~~~~~~~~

Don't forget to commit and tag your Project 7 code::

     bash % git commit -m "Project 7 complete"
     bash % git tag project7

This next stage of the project is the most difficult of all.   Failure
to commit your previously "working" code is not advised.

Overview
~~~~~~~~

Full disclaimer:  This part of the project is probably the most difficult to
implement and will probably require a day of work.  You will need to
make changes to virtually every part of the compiler to do it.

In this project, you are going to give your compiler support for user
defined functions.  For example::

    // External function definition
    import func sin(x float) float;

    // Function definition
    func add(x int, y int) int {
         return x+y;
    }

    // Function definition
    func fibonacci(n int) int {
         if n > 1 {
            return fibonacci(n-1) + fibonacci(n-2);     // Return
         } else {
            return 1;    // Return
         }
         return 0;   // Might need this (depends on how smart compiler is)
     }

     const MAXFIB = 20;       // Global

     // Function definition (entry point)    
     func main() int {
          print add(2,3);            // Function call
          print sin(3);              // External call
          var n int;
          while n < MAXFIB {
              print fibonacci(n);    // Function call
          }
          return 0;
     }

Here are the main features that you are going to implement:

1. Function definitions via the ``func`` keyword.
2. The ability to return a value from a function using ``return``.
3. Global and local scoping rules for variables.
4. Calling of main() function as the program entry point
5. Ability to import foreign functions using the ``import`` keyword.

There are many different steps involved.  Here is the order
in which you should probably work on it:

1. Add new tokens for ``func``, ``import``, and ``return`` to the lexer.

2. Define some new AST nodes corresponding to a function definition,
function call, and the return statement.  You may need to introduce
additional AST nodes for function parameters, parameter lists,
arguments, and argument expression lists.
   
3. Add new parsing rules to your parser for all of the new AST nodes.
Specifically, you need to support function definitions, function call,
and return statements.

4. Modify the type checking code to use two-level scoping.  For
instance, instead of having just a single symbol table, define a
global symbol table and a local symbol table for use when inside
a function body.  Modify the code that stores symbols to use the
appropriate symbol table depending on content.  Modify the code that
looks up symbols to consult both symbol tables.   You may also want to
store additional information on declarations to indicate whether or
not they are global or local (this will provide to be useful later
during code generation).

5. Add new type checking rules for all of the new AST nodes. This
type checking may include:

   a. Check that function names are defined.
   b. Check that a name corresponds to a function declaration.
   c. Not allowing nested function definitions.
   d. Making sure the number of arguments and types match in function calls.
   e. Making sure the value returned by a function matches the function return type.
   f. Making sure local variable names can refer to function parameters.

6. Extend the intermediate code so that it understands the distinction
between local and global variables.   For example, maybe you now how two
variable operations::

    ('VARI', name)          # Allocate a local variable
    ('GLOBALI', name)       # Allocate a global variable

You'll also need instructions for function call and return::

    ('CALL', name)          # Call a function (arguments on stack)
    ('RETURN',)             # Return (return value on stack)

7. Modify code generation so that each function declaration is parsed into
its own set of instruction blocks.  The code generator should collect all of
the resulting code fragments (e.g., you should make a list consisting of
the name of a function, function parameter information, followed by the
list of the instructions making up the function body).
function body).

8. Extend the control-flow analysis code to detect functions that
end without some kind of return statement (i.e., functions that
just fall off the end).  (optional)

9. Have the code generator collect code that doesn't belong in any
proper function definition and put it into a special initialization
function called ``__init__()``.  This step is needed to handle things such as the
initialization of global variable values.

10. Modify the Wasm and LLVM code generators to emit code for all 
of the functions that are defined.  You'll need to make a variety
of changes for this including support for global variables, function
calls, and invocation of the special ``__init()`` function that
initializes the environment. For Wasm, you may need to add a few
new sections to the output module.  See details below for more information.
   
General Advice
~~~~~~~~~~~~~~

Success with this part of the project requires careful and methodical work. 
Don't worry about rushing through everything.  Just take it one step at a time.
Test things as you go. For a long time it will seem like you aren't making
any progress, but then it will just suddenly come together at the end.

Testing
~~~~~~~

The following files are available::

     Tests/func.wb                # Some simple functions
     Tests/funcerrors.wb          # Common errors involving functions
     Tests/funcret.wb             # Tests for missing return statements

Real Programs
~~~~~~~~~~~~~

The ``Programs/`` directory has a collection of Wabbit programs that
you can try with your final compiler.  For example, making a Mandelbrot
set::

     bash % python3 -m wabbit.run Programs/mandel.wb
     ... look at the output ...

LLVM Implementation Notes
~~~~~~~~~~~~~~~~~~~~~~~~~
In past work, variables in LLVM were declared as local variables. For example::

     y_var = builder.alloca(IntType(32), name='y')
     builder.store(Constant(IntType(32), 0), y_var)

Once you start having functions, you'll have both local and global variables.
For example::

     var int x = 0;          // Global variable
     func spam(a int) int {
         var int y;          // Local variable
    
     }

Global variables should be declared differently::

     x_var = GlobalVariable(mod, IntType(32), name='x')
     x_var.initializer = Constant(IntType(32), 0)

As with type-checking, you're going to need two different scopes to
keep track of local/global names.  However, as long as you refer to
the correct object, other instructions such as ``load`` and ``store``
should continue to work.

Within functions, you're going to need to properly bind the function arguments
to local variables.   On any function, the `args` attribute has the arguments.
You'll need to do something like this at the start of each function::

     for n, (argname, argtype) in enumerate(zip(argnames, argtypes)):
         self.vars[argname] = self.builder.alloca(argtype, name=argname)
         self.builder.store(func.args[n], self.vars[argname])

To call a function in LLVM, you use the ``builder.call()`` instruction::

    result = builder.call(func, [args])

As an argument, you need to supply all of the argument values in a list.
Since we're working with a stack-based intermediate code, you're going to need
to pull the arguments off the stack.  You'll need to know the argument count
to do it.  Thus, the code might look like this::

    args = [self.pop() for _ in range(len(func.args))][::-1]   # Must reverse
    self.push(builder.call(func, args))

Web Assembly Implementation Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will need to manage local and global variables in separate spaces.
Global variables are encoded into a dedicated section 6 in the Wasm
module structure.  This is a new section of the encoding not seen before.
You'll have to figure out the encoding for it.  Like with functions and types,
globals are assigned a numeric index.  Any reference to a global variable
uses the numeric index.   There are dedicated instructions ``global.get``
and ``global.set`` for accessing globals.

When encoding, all functions get a unique numerical index (``funcidx``).  All
imported functions always get listed first, starting at zero.  Functions
defined within the Wasm module itself get indices that start after all
imports have been declared.   When putting together the Wasm module, you'll
need to make sure all imported functions always get processed first.

All local variables in Wasm also get assigned a numeric index.  However,
function parameters always go first.   Thus, function parameters are
local variables starting with index 0.  After all parameters, then the local
variables get added.   So, if you had this function::

    func spam(x int, y int) int {
        var a int = x + y;
        var b int = 2 * a;
        return b;
    }

The local variables and their indices would be this::

    'x':   index=0
    'y':   index=1
    'a':   index=2
    'b':   index=3

Function arguments are NOT incuded in the function body encoding
(the data in section 10 of the Wasm module). 
Only the local variables appear.  The function parameters are already
known because they're part of the function type signature (which is
encoded separately). 

If you're getting a lot of validation errors about bad types, there's
a good chance you've got your function/local/global index values set wrong.
