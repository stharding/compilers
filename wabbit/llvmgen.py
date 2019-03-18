# llvmgen.py
'''
Generate LLVM
=============

This code generator translates the intermediate code into LLVM IR.
It is strongly advised that you do *all* of the steps of Exercise 5
prior to starting this project.

Further instructions are contained in the comments below.
'''
from collections import ChainMap

# LLVM imports. Don't change this.

from llvmlite.ir import (
    Module, IRBuilder, Function, IntType, DoubleType, VoidType, Constant, GlobalVariable,
    FunctionType
    )

# Declare the LLVM type objects that you want to use for the low-level
# in our intermediate code.  Basically, you're going to need to
# declare the integer, float, and char types here.  These correspond
# to the types being used the intermediate code being created by
# the ircode.py file.

int_type    = IntType(32)         # 32-bit integer
float_type  = DoubleType()        # 64-bit float
void_type   = VoidType()          # Void type.  This is a special type
                                  # used for internal functions returning
                                  # no value

# Mapping of Wabbit names to LLVM types
typemap = {
    'int': int_type,
    'float' : float_type,
    'char': int_type,
    None: void_type
}

# The following class is going to generate the LLVM instruction stream.  
# The basic features of this class are going to mirror the experiments
# you tried in Exercise 5.  The execution model is somewhat similar
# to the visitor class.
#
# Given a sequence of instruction tuples such as this:
#
#         code = [ 
#              ('CONSTI', 1),
#              ('CONSTI', 2),
#              ('ADDI',),
#              ('PRINTI',),
#              ...
#         ]
#
#    The class executes methods self.emit_opcode(args).  For example:
#
#             self.emit_CONSTI(1)
#             self.emit_CONSTI(2)
#             self.emit_ADDI()
#             self.emit_PRINTI()
#
#    Internally, you're going to need to keep an internal stack to keep
#    track of LLVM temporaries being created.  Stack operations will
#    carry out the appropriate operations on those temporaries.

class GenerateLLVM(object):
    def __init__(self):
        # Perform the basic LLVM initialization.  You need the following parts:
        #
        #    1.  A top-level Module object
        #    2.  A dictionary of global declarations
        #    3.  Initialization of runtime functions (for printing)
        #
        self.module = Module('module')

        # Dictionary that holds all of the global variable/function declarations.
        # Any declaration in the Wabbit source code is going to get an entry here
        self.globals = {}

        # Initialize the runtime library functions (see below)
        self.declare_runtime_library()

    def declare_runtime_library(self):
        # Certain functions such as I/O and string handling are often easier
        # to implement in an external C library.  This method should make
        # the LLVM declarations for any runtime functions to be used
        # during code generation.    Please note that runtime function
        # functions are implemented in C in a separate file wabbitrt.c

        self.runtime = {}

        # Declare runtime functions
        functions = [
            ('_print_int', void_type, [int_type]),
            ('_print_float', void_type, [float_type]),
            ('_print_byte', void_type, [int_type]),
            ]
        for name, rettype, args in functions:
            self.runtime[name] = Function(self.module,
                                          FunctionType(rettype, args),
                                          name=name)

    def declare_function(self, funcname, argtypes, rettype):
        self.function = Function(self.module,
                                 FunctionType(rettype, argtypes),
                                 name=funcname)

        # Insert a reference in global namespace
        self.globals[funcname] = self.function

    def generate_function(self, funcname, argnames, ircode):
        # Generate code for a single Wabbit function. Each opcode
        # tuple (opcode, args) is dispatched to a method of the form
        # self.emit_opcode(args). Function should already be declared 
        # using declare_function.
        
        self.function = self.globals[funcname]
        self.block = self.function.append_basic_block('entry')
        self.builder = IRBuilder(self.block)

        # Stack of LLVM temporaries
        self.stack = [] 

        # Dictionary of local variables
        self.locals = { }

        for opcode, *opargs in ircode:
            if hasattr(self, 'emit_'+opcode):
                getattr(self, 'emit_'+opcode)(*opargs)
            else:
                print('Warning: No emit_'+opcode+'() method')

        # Add a return statement to void functions.
        if self.function.function_type.return_type == void_type:
            self.builder.ret_void()

    # Helper methods for LLVM temporary stack manipulation
    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_CONSTI(self, value):
        self.push(Constant(int_type, value))

    def emit_CONSTF(self, value):
        pass  # You must implement

    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_VARI(self, name):
        self.locals[name] = self.builder.alloca(int_type, name=name)

    def emit_VARF(self, name):
        pass  # You must implement
        
    # Load/store instructions for variables.  
    def emit_LOAD(self, name):
        self.push(self.builder.load(self.locals[name], name))

    def emit_STORE(self, name):
        self.builder.store(self.pop(), self.locals[name])

    # Binary + operator
    def emit_ADDI(self):
        self.push(self.builder.add(self.pop(), self.pop()))

    def emit_ADDF(self):
        pass  # You must implement

    # Binary - operator
    def emit_SUBI(self):
        pass  # You must implement

    def emit_SUBF(self):
        pass  # You must implement

    # Binary * operator
    def emit_MULI(self):
        pass  # You must implement

    def emit_MULF(self):
        pass  # You must implement

    # Binary / operator
    def emit_DIVI(self):
        pass  # You must implement

    def emit_DIVF(self):
        pass  # You must implement

    # Conversion
    def emit_ITOF(self):
        self.push(self.builder.sitofp(self.pop(), float_type))

    def emit_FTOI(self):
        pass  # You must implement

    # Print statements
    def emit_PRINTI(self):
        self.builder.call(self.runtime['_print_int'], [self.pop()])

    def emit_PRINTF(self):
        pass  # You must implement

    def emit_PRINTB(self):
        pass  # You must implement

    # Memory statements
    def emit_GROW(self):
        pass  # You must implement

    def emit_PEEKI(self):
        pass  # You must implement

    def emit_PEEKF(self):
        pass  # You must implement

    def emit_PEEKB(self):
        pass  # You must implement

    def emit_POKEI(self):
        pass  # You must implement

    def emit_POKEF(self):
        pass  # You must implement

    def emit_POKEB(self):
        pass  # You must implement

#######################################################################
#                      TESTING/MAIN PROGRAM
#######################################################################

def compile_llvm(source):
    from .ircode import compile_ircode

    # Compile intermediate code 
    code = compile_ircode(source)
    if code:
        # Make the low-level code generator
        generator = GenerateLLVM()
        generator.declare_function("main", [], void_type)
        generator.generate_function("main", [], code)
        return str(generator.module)
    else:
        return ''

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m wabbit.llvmgen filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    print(llvm_code)

if __name__ == '__main__':
    main()



        
        
        
