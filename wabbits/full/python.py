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
        # The stack
        self.stack = [ ]
        self.indent = '    '
        self.funcargs = { }

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def import_function(self, funcname, args):
        self.funcargs[funcname] = len(args)
        return f'from _wabbit import {funcname}\n'

    def transpile(self, funcname, args, code):
        self.funcargs[funcname] = len(args)
        argstr = ','.join(args)
        self.pycode = f'def {funcname}({argstr}):\n'
        self.stack = []
        self.indent = '    '

        for inst, *args in code:
            getattr(self, f'translate_{inst}')(*args)

        if not code:
            self.pycode +='    pass\n'

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

    def translate_LEI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left}<={right})')

    translate_LEF = translate_LEI

    def translate_LTI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left}<{right})')

    translate_LTF = translate_LTI

    def translate_GEI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left}>={right})')

    translate_GEF = translate_GEI

    def translate_GTI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left}>{right})')

    translate_GTF = translate_GTI

    def translate_EQI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left}=={right})')

    translate_EQF = translate_EQI

    def translate_NEI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left}!={right})')

    translate_NEF = translate_NEI        

    def translate_ANDI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left} & {right})')

    def translate_ORI(self):
        right = self.pop()
        left = self.pop()
        self.push(f'int({left} | {right})')

    def translate_PRINTI(self):
        self.pycode += f'{self.indent}print({self.pop()})\n'
    translate_PRINTF = translate_PRINTI

    def translate_PRINTB(self):
        self.pycode += f'{self.indent}print(chr({self.pop()}),end="")\n'

    def translate_VARI(self, name):
        self.pycode += f'{self.indent}{name} = 0\n'

    def translate_VARF(self, name):
        self.pycode += f'{self.indent}{name} = 0.0\n'

    def translate_GLOBALI(self, name):
        self.pycode += f'{self.indent}global {name}\n'

    translate_GLOBALF = translate_GLOBALI

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
        
    # Control flow
    def translate_IF(self):
        self.pycode += f'{self.indent}if {self.pop()}:\n'
        self.indent += '    '

    def translate_ELSE(self):
        self.indent = self.indent[:-4]
        self.pycode += f'{self.indent}else:\n'
        self.indent += '    '
        self.pycode += f'{self.indent}pass\n'

    def translate_ENDIF(self):
        self.indent = self.indent[:-4]

    def translate_LOOP(self):
        self.pycode += f'{self.indent}while 1:\n'
        self.indent += '    '

    def translate_CBREAK(self):
        self.pycode += f'{self.indent}if {self.pop()}: break\n'
        
    def translate_ENDLOOP(self):
        self.indent = self.indent[:-4]

    def translate_RETURN(self):
        self.pycode += f'{self.indent}return {self.pop()}\n'

    def translate_CALL(self, name):
        argcount = self.funcargs[name]
        args = [self.pop() for _ in range(argcount)][::-1]
        argstr=','.join(args)
        self.push(f'{name}({argstr})')

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def transpile_python(source):
    from .ircode import compile_ircode
    from .errors import errors_reported
    module = compile_ircode(source)
    if module:
        code = 'import struct\n' \
               '_memory = bytearray()\n'

        transpiler = Transpiler()
        has_main = False
        for func in module.imports:
            argnames = [arg[0] for arg in func.parameters]
            code += transpiler.import_function(func.name, argnames)

        for func in module.functions:
            if func.name == 'main':
                has_main = True

            argnames = [arg[0] for arg in func.parameters]
            code += transpiler.transpile(func.name, argnames, func)
            code += '\n'

        if not has_main:
           code += 'def main(): pass\n'

        code += '__init(); main()\n'
        return code

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






        
        
        
