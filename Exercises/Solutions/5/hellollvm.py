# hellollvm.py

from llvmlite.ir import (
    Module, Function, FunctionType, IntType, VoidType,
    Constant, IRBuilder
    )

mod = Module('hello')

int_type = IntType(32)
void_type = VoidType()

_print_int = Function(mod, 
                      FunctionType(void_type, [int_type]), 
                      name='_print_int')

hello_func = Function(mod, FunctionType(int_type, []), name='hello')
block = hello_func.append_basic_block('entry')
builder = IRBuilder(block)

x = builder.alloca(int_type, name='x')
y = builder.alloca(int_type, name='y')
builder.store(Constant(int_type, 4), x)
builder.store(Constant(int_type, 5), y)
t1 = builder.load(x)
t2 = builder.load(x)
t3 = builder.mul(t1, t2)
t4 = builder.load(y)
t5 = builder.load(y)
t6 = builder.mul(t4, t5)
t7 = builder.add(t3, t6)
d = builder.alloca(int_type, name='d')
builder.store(t7, d)
builder.call(_print_int, [builder.load(d)])
builder.ret(Constant(int_type, 37))
print(mod)

def run_jit(module):
    import llvmlite.binding as llvm

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    compiled_mod = llvm.parse_assembly(str(module))
    engine = llvm.create_mcjit_compiler(compiled_mod, target_machine)

    # Look up the function pointer (a Python int)
    func_ptr = engine.get_function_address("hello")

    # Turn into a Python callable using ctypes
    from ctypes import CFUNCTYPE, c_int
    hello = CFUNCTYPE(c_int)(func_ptr)

    res = hello()
    print('hello() returned', res)

# run_jit(mod)
