# python.py
'''
Transpiler Project
==================

This module transpiles Wabbit IR code to a Python function.
To do this use:

    bash % python3 -m wabbit.python someprogram.wb

This should write a file 'out.py' in the current directory.
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

    def translate_ADDI(self):
        self.push(f'({self.pop()}+{self.pop()})')

    def translate_PRINTI(self):
        self.pycode += f'{self.indent}print({self.pop()})\n'

    def translate_VARI(self, name):
        self.pycode += f'{self.indent}{name} = 0\n'
        
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






        
        
        
