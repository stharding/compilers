# python.py
'''
Transpiler Project
==================

This module transpiles Wabbit IR code to a Python function.
To do this use:

    bash % python3 -m wabbit.python someprogram.wb

This should write a file 'someprogram.py' in the current directory.
Within that directory will be a functions containing translated
Wabbit code.
'''

import sys
        
class Transpiler:
    '''
    Runs a transpiler on the intermediate code generated for
    your compiler.   The implementation idea is as follows.  Given
    a sequence of instruction tuples such as:

         code = [ 
              ('CONSTI', 1),
              ('CONSTI', 2),
              ('ADDI',),
              ('PRINTI',)
              ...
         ]

    The class generates Python code such as this:

        def main():
            print(1+2)
   
    You may have deal with some tricky syntax issues with Python
    indentation.
    '''
    def __init__(self):
        self.indent = '    '

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def transpile(self, funcname, args, code):
        argstr = ','.join(args)
        self.pycode = f'def {funcname}({argstr}):\n'
        self.stack = []
        self.indent = '    '

        for inst, *args in code:
            getattr(self, f'translate_{inst}')(*args)

        return self.pycode
        
    # Interpreter opcodes
    def translate_CONSTI(self, value):
        self.push(repr(value))
    translate_CONSTF = translate_CONSTI

    def translate_ADDI(self):
        self.push(f'({self.pop()}+{self.pop()})')
    translate_ADDF = translate_ADDI

    def translate_SUBI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'({left}-{right})')
    translate_SUBF = translate_SUBI

    def translate_MULI(self):
        self.push(f'({self.pop()}*{self.pop()})')
    translate_MULF = translate_MULI

    def translate_DIVI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'({left}//{right})')

    def translate_DIVF(self):
        right = self.pop()
        left = self.pop()
        self.push(f'({left}/{right})')

    def translate_ITOF(self):
        self.push(f'float({self.pop()})')

    def translate_FTOI(self):
        self.push(f'int({self.pop()})')

    def translate_PRINTI(self):
        self.pycode += f'{self.indent}print({self.pop()})\n'
    translate_PRINTF = translate_PRINTI

    def translate_PRINTB(self):
        self.pycode += f'{self.indent}print(chr({self.pop()}),end="")\n'

    def translate_VARI(self, name):
        self.pycode += f'{self.indent}{name} = 0\n'

    def translate_VARF(self, name):
        self.pycode += f'{self.indent}{name} = 0.0\n'

    def translate_LOAD(self, name):
        self.push(name)

    def translate_STORE(self, name):
        self.pycode += f'{self.indent}{name} = {self.pop()}\n'

    def translate_GROW(self):
        self.push(f'(_memory.extend(b"\\x00"*{self.pop()}), len(_memory))[1]')

    def translate_PEEKI(self):
        addr = self.pop()
        self.push(f'struct.unpack("<i", _memory[{addr}:{addr}+4])[0]')

    def translate_PEEKF(self):
        addr = self.pop()
        self.push(f'struct.unpack("<d", _memory[{addr}:{addr}+8])[0]')

    def translate_PEEKB(self):
        self.push(f'_memory[{self.pop()}]')

    def translate_POKEI(self):
        value = self.pop()
        addr = self.pop()
        self.pycode += f'{self.indent}_memory[{addr}:{addr}+4] = struct.pack("<i", {value})\n'

    def translate_POKEF(self):
        value = self.pop()
        addr = self.pop()
        self.pycode += f'{self.indent}_memory[{addr}:{addr}+8] = struct.pack("<d", {value})\n'

    def translate_POKEB(self):
        value = self.pop()
        addr = self.pop()
        self.pycode += f'{self.indent}_memory[{addr}] = {value}\n'
        
# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def transpile_python(source):
    from .ircode import compile_ircode
    from .errors import errors_reported
    code = compile_ircode(source)
    if code:
        pycode = 'import struct\n' \
                 '_memory = bytearray()\n'

        transpiler = Transpiler()
        pycode += transpiler.transpile("main", [], code)
        pycode += 'main()\n'
        return pycode

def main():
    import sys
    from pathlib import Path

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m wabbit.python filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = transpile_python(source)
    if code:
        with open('out.py', 'wt') as file:
            file.write(code)

if __name__ == '__main__':
    main()






        
        
        
