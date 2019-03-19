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
    'bool': int_type,
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
            ('_grow', int_type, [int_type]),
            ('_peeki', int_type, [int_type]),
            ('_peekf', float_type, [int_type]),
            ('_peekb', int_type, [int_type]),
            ('_pokei', void_type, [int_type, int_type]),
            ('_pokef', void_type, [int_type, float_type]),
            ('_pokeb', void_type, [int_type, int_type]),
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

        # Combined symbol table
        self.symbols = ChainMap(self.locals, self.globals)

        # Have to declare local variables for holding function arguments
        for n, (name, ty) in enumerate(zip(argnames, self.function.function_type.args)):
            self.locals[name] = self.builder.alloca(ty, name=name)
            self.builder.store(self.function.args[n], self.locals[name])

        # Stack of blocks
        self.blocks = [ ]

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

    def set_block(self, block):
        self.block = block
        self.builder.position_at_end(self.block)

    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_CONSTI(self, value):
        self.push(Constant(int_type, value))

    def emit_CONSTF(self, value):
        self.push(Constant(float_type, value))

    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_VARI(self, name):
        self.locals[name] = self.builder.alloca(int_type, name=name)

    def emit_VARF(self, name):
        self.locals[name] = self.builder.alloca(float_type, name=name)

    # Allocation of globals
    def emit_GLOBALI(self, name):
        var = GlobalVariable(self.module, int_type, name=name)
        var.initializer = Constant(int_type, 0)
        self.globals[name] = var

    def emit_GLOBALF(self, name):
        var = GlobalVariable(self.module, float_type, name=name)
        var.initializer = Constant(float_type, 0.0)
        self.globals[name] = var
        
    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def emit_LOAD(self, name):
        self.push(self.builder.load(self.symbols[name], name))

    def emit_STORE(self, target):
        self.builder.store(self.pop(), self.symbols[target])

    # Binary + operator
    def emit_ADDI(self):
        self.push(self.builder.add(self.pop(), self.pop()))

    def emit_ADDF(self):
        self.push(self.builder.fadd(self.pop(), self.pop()))

    # Binary - operator
    def emit_SUBI(self):
        right = self.pop()
        left = self.pop()
        self.push(self.builder.sub(left, right))

    def emit_SUBF(self):
        right = self.pop()
        left = self.pop()
        self.push(self.builder.fsub(left, right))

    # Binary * operator
    def emit_MULI(self):
        self.push(self.builder.mul(self.pop(), self.pop()))

    def emit_MULF(self):
        self.push(self.builder.fmul(self.pop(), self.pop()))

    # Binary / operator
    def emit_DIVI(self):
        right = self.pop()
        left = self.pop()
        self.push(self.builder.sdiv(left, right))

    def emit_DIVF(self):
        right = self.pop()
        left = self.pop()
        self.push(self.builder.fdiv(left, right))

    # Conversion
    def emit_ITOF(self):
        self.push(self.builder.sitofp(self.pop(), float_type))

    def emit_FTOI(self):
        self.push(self.builder.fptosi(self.pop(), int_type))

    # Comparison operators
    def emit_LEI(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.icmp_signed('<=', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_LTI(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.icmp_signed('<', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_GEI(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.icmp_signed('>=', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_GTI(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.icmp_signed('>', left, right)
        self.push(self.builder.zext(result, int_type))
        
    def emit_EQI(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.icmp_signed('==', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_NEI(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.icmp_signed('!=', left, right)
        self.push(self.builder.zext(result, int_type))

    # Comparison operators
    def emit_LEF(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.fcmp_ordered('<=', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_LTF(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.fcmp_ordered('<', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_GEF(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.fcmp_ordered('>=', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_GTF(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.fcmp_ordered('>', left, right)
        self.push(self.builder.zext(result, int_type))
        
    def emit_EQF(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.fcmp_ordered('==', left, right)
        self.push(self.builder.zext(result, int_type))

    def emit_NEF(self):
        right = self.pop()
        left = self.pop()
        result = self.builder.fcmp_ordered('!=', left, right)
        self.push(self.builder.zext(result, int_type))

    # Bitwise operations

    def emit_ANDI(self):
        right = self.pop()
        left = self.pop()
        self.push(self.builder.and_(left, right))

    def emit_ORI(self):
        right = self.pop()
        left = self.pop()
        self.push(self.builder.or_(left, right))
        
    # Print statements
    def emit_PRINTI(self):
        self.builder.call(self.runtime['_print_int'], [self.pop()])

    def emit_PRINTF(self):
        self.builder.call(self.runtime['_print_float'], [self.pop()])

    def emit_PRINTB(self):
        self.builder.call(self.runtime['_print_byte'], [self.pop()])

    # Memory statements
    def emit_GROW(self):
        self.push(self.builder.call(self.runtime['_grow'], [self.pop()]))

    def emit_PEEKI(self):
        self.push(self.builder.call(self.runtime['_peeki'], [self.pop()]))

    def emit_PEEKF(self):
        self.push(self.builder.call(self.runtime['_peekf'], [self.pop()]))

    def emit_PEEKB(self):
        self.push(self.builder.call(self.runtime['_peekb'], [self.pop()]))

    def emit_POKEI(self):
        value = self.pop()
        addr = self.pop()
        self.builder.call(self.runtime['_pokei'], [addr, value])

    def emit_POKEF(self):
        value = self.pop()
        addr = self.pop()
        self.builder.call(self.runtime['_pokef'], [addr, value])

    def emit_POKEB(self):
        value = self.pop()
        addr = self.pop()
        self.builder.call(self.runtime['_pokeb'], [addr, value])

    # Control flow
    def emit_IF(self):
        then_block = self.function.append_basic_block()
        else_block = self.function.append_basic_block()
        exit_block = self.function.append_basic_block()
        self.builder.cbranch(self.builder.trunc(self.pop(), IntType(1)), then_block, else_block)
        self.set_block(then_block)
        self.blocks.append([then_block, else_block, exit_block])

    def emit_ELSE(self):
        if not self.block.is_terminated:
            self.builder.branch(self.blocks[-1][2])
        self.set_block(self.blocks[-1][1])

    def emit_ENDIF(self):
        if not self.block.is_terminated:
            self.builder.branch(self.blocks[-1][2])
        self.set_block(self.blocks[-1][2])
        self.blocks.pop()

    def emit_LOOP(self):
        top_block = self.function.append_basic_block()
        exit_block = self.function.append_basic_block()
        self.builder.branch(top_block)
        self.set_block(top_block)
        self.blocks.append([top_block, exit_block])

    def emit_CBREAK(self):
        next_block = self.function.append_basic_block()
        self.builder.cbranch(self.builder.trunc(self.pop(), IntType(1)), self.blocks[-1][1], next_block)
        self.set_block(next_block)
        
    def emit_ENDLOOP(self):
        if not self.block.is_terminated:
            self.builder.branch(self.blocks[-1][0])
        self.set_block(self.blocks[-1][1])
        self.blocks.pop()

    def emit_RETURN(self):
        self.builder.ret(self.pop())

    def emit_CALL(self, name):
        func = self.globals[name]
        args = [self.pop() for _ in range(len(func.args))][::-1]
        self.push(self.builder.call(func, args))

#######################################################################
#                      TESTING/MAIN PROGRAM
#######################################################################

def compile_llvm(source):
    from .ircode import compile_ircode

    # Compile intermediate code 
    module = compile_ircode(source)
    if module:
        # Make the low-level code generator
        generator = GenerateLLVM()

        # Declare all functions first
        has_main = False
        for func in [*module.functions, *module.imports]:
            argtypes = []
            for name, ty in func.parameters:
                argtypes.append(typemap[ty])
            rettype = typemap[func.rettype]
            generator.declare_function(func.name, argtypes, rettype)
            if func.name == 'main':
                has_main = True
            
        # Generate low-level code for defined functions
        for func in module.functions:
            argnames = [parm[0] for parm in func.parameters]
            # Hack alert. If the 'main' function, we need to inject a call to __init into
            # the instruction stream
            if func.name == 'main':
                func.code = [ ('CALL', '__init'), *func]
            generator.generate_function(func.name, argnames, func)

        if not has_main:
            generator.declare_function('main', [], void_type)
            generator.generate_function('main', [], [ ('CALL', '__init') ])

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



        
        
        
