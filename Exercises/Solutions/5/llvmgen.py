# llvmgen.py

code = [
    ('VARI', 'x'),
    ('CONSTI', 4),
    ('STORE', 'x'),
    ('VARI', 'y'),
    ('CONSTI', 5),
    ('STORE', 'y'),
    ('VARI', 'd'),
    ('LOAD', 'x'),
    ('LOAD', 'x'),
    ('MULI',),
    ('LOAD', 'y'),
    ('LOAD', 'y'),
    ('MULI',),
    ('ADDI',),
    ('STORE', 'd'),
    ('LOAD', 'd'),
    ('PRINTI',)
]

from llvmlite.ir import (
    Module, Function, FunctionType, IntType, VoidType,
    Constant, IRBuilder
    )

int_type = IntType(32)
void_type = VoidType()

class LLVMGenerator:
    def __init__(self):
        self.module = Module('hello')
        self._print_int = Function(self.module, 
                                   FunctionType(void_type, [int_type]), 
                                   name='_print_int')

        self.function = Function(self.module,
                                 FunctionType(int_type, []), 
                                 name='main')
        self.block = self.function.append_basic_block('entry')
        self.builder = IRBuilder(self.block)

        self.stack = [ ]
        self.vars = { }

    def emit(self, code):
        for op, *opargs in code:
            getattr(self, f'emit_{op}')(*opargs)
        self.builder.ret(Constant(int_type, 0))
        return str(self.module)

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def emit_VARI(self, name):
        self.vars[name] = self.builder.alloca(int_type, name=name)

    def emit_CONSTI(self, value):
        self.push(Constant(int_type, value))

    def emit_STORE(self, name):
        self.builder.store(self.pop(), self.vars[name])

    def emit_LOAD(self, name):
        self.push(self.builder.load(self.vars[name]))

    def emit_ADDI(self):
        self.push(self.builder.add(self.pop(), self.pop()))

    def emit_MULI(self):
        self.push(self.builder.mul(self.pop(), self.pop()))

    def emit_PRINTI(self):
        self.builder.call(self._print_int, [self.pop()])

gen = LLVMGenerator()
print(gen.emit(code))

