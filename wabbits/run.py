# run.py
#
# Project 5:
# ----------
# Runs a Wabbit program in a LLVM JIT.   This requires that the
# Wabbit runtime support library (wabbitrt.c) be compiled into a shared
# object and placed in the same directory as this file.
#
# Note:  This project will require minor modification in Project 8

import os
import os.path
import ctypes
import llvmlite.binding as llvm

_path = os.path.dirname(__file__)

def run(llvm_ir):
    # Load the runtime
    if os.name != 'nt':
        ctypes._dlopen(os.path.join(_path, 'wabbitrt.so'), ctypes.RTLD_GLOBAL)
    else:
        ctypes._dlopen(os.path.join(_path, 'wabbitrt.dll'), ctypes.RTLD_GLOBAL)

    # Initialize LLVM
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()

    engine = llvm.create_mcjit_compiler(mod, target_machine)

    # Execute the main() function
    #
    # !!! Note: May requires modification in Project 8
    main_ptr = engine.get_function_address('main')
    main_func = ctypes.CFUNCTYPE(None)(main_ptr)
    main_func()

    # Project 8:  Modify the above code to execute any __init()
    # function that initializes global variables.

def main():
    from .errors import errors_reported
    from .llvmgen import compile_llvm
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m wabbit.run filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    if not errors_reported():
        run(llvm_code)

if __name__ == '__main__':
    main()
