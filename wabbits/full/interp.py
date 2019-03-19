# interp.py
'''
Interpreter Project
===================

This is an interpreter than can run wabbit programs directly from the
generated IR code.  

To run a program use::

    bash % python3 -m wabbit.interp someprogram.wb

'''
import sys
import struct
        
class Interpreter(object):
    '''
    Runs an interpreter on the intermediate code generated for
    your compiler.   The implementation idea is as follows.  Given
    a sequence of instruction tuples such as:

         code = [ 
              ('CONSTI', 1),
              ('CONSTI', 2),
              ('ADDI',),
              ('PRINTI',)
              ...
         ]

    The class executes methods self.run_opcode(args).  For example:

             self.run_CONSTI(1)
             self.run_CONSTI(2)
             self.run_ADDI()
             self.run_PRINTI()

    Just a reminder that the intermediate code is based on a stack machine.
    The interpreter needs to implement the stack as well as memory
    for storing variables.
    '''
    def __init__(self):
        self.code = []
        self.pc = 0

        # Variable storage
        self.globals = { }
        self.vars = { }

        # Stack frames stack
        self.frames = [ ]

        # The operation stack
        self.stack = [ ]

        # Memory
        self.memory = bytearray()

        # Control-flow labels
        self.control = { }

        # Function table
        self.functions = { }

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def add_function(self, name, argnames, code):
        # Figure out control flow labels
        control = { }
        levels = []
        for n, (inst, *args) in enumerate(code):
            if inst == 'IF':
                levels.append(n)
            elif inst == 'ELSE':
                control[levels[-1]] = n
                levels[-1] = n
            elif inst == 'ENDIF':
                control[levels[-1]] = n
                levels.pop()
            if inst == 'LOOP':
                levels.append(n)
            elif inst == 'CBREAK':
                levels.append(n)
            elif inst == 'ENDLOOP':
                control[n] = levels[-2]
                control[levels[-1]] = n
                levels.pop()
                levels.pop()
        self.functions[name] = (code, argnames, control)

    def execute(self, name):
        self.frames.append((self.code, self.pc, self.control, self.vars))
        self.code, argnames, self.control = self.functions[name]
        self.vars = { }

        # Pull argument values off the stack
        for argname in argnames[::-1]:
            value = self.pop()
            self.vars[argname] = value

        self.pc = 0
        while self.pc < len(self.code):
            inst, *args = self.code[self.pc]
            getattr(self, f'run_{inst}')(*args)
            self.pc += 1
        self.code, self.pc, self.control, self.vars = self.frames.pop()
        
    # Interpreter opcodes
    def run_CONSTI(self, value):
        self.push(value)
    run_CONSTF = run_CONSTI

    def run_ADDI(self):
        self.push(self.pop() + self.pop())
    run_ADDF = run_ADDI

    def run_SUBI(self):
        right = self.pop()
        left = self.pop()
        self.push(left-right)
    run_SUBF = run_SUBI

    def run_MULI(self):
        self.push(self.pop() * self.pop())
    run_MULF = run_MULI

    def run_DIVI(self):
        right = self.pop()
        left = self.pop()
        self.push(left // right)

    def run_DIVF(self):
        right = self.pop()
        left = self.pop()
        self.push(left / right)

    def run_ITOF(self):
        self.push(float(self.pop()))

    def run_FTOI(self):
        self.push(int(self.pop()))

    def run_PRINTI(self):
        print(self.pop())
    run_PRINTF = run_PRINTI

    def run_PRINTB(self):
        print(chr(self.pop()),end='')

    def run_VARI(self, name):
        self.vars[name] = 0

    def run_VARF(self, name):
        self.vars[name] = 0.0

    def run_GLOBALI(self, name):
        self.globals[name] = None

    def run_GLOBALF(self, name):
        self.globals[name] = None

    def run_LOAD(self, name):
        if name in self.vars:
            self.push(self.vars[name])
        else:
            self.push(self.globals[name])

    def run_STORE(self, name):
        if name in self.vars:
            self.vars[name] = self.pop()
        else:
            self.globals[name] = self.pop()

    def run_LEI(self):
        right = self.pop()
        left = self.pop()
        self.push(int(left <= right))

    run_LEF = run_LEI

    def run_LTI(self):
        right = self.pop()
        left = self.pop()
        self.push(int(left < right))

    run_LTF = run_LTI

    def run_GEI(self):
        right = self.pop()
        left = self.pop()
        self.push(int(left >= right))

    run_GEF = run_GEI

    def run_GTI(self):
        right = self.pop()
        left = self.pop()
        self.push(int(left > right))

    run_GTF = run_GTI

    def run_EQI(self):
        right = self.pop()
        left = self.pop()
        self.push(int(left == right))

    run_EQF = run_EQI

    def run_NEI(self):
        right = self.pop()
        left = self.pop()
        self.push(int(left != right))

    run_NEF = run_NEI

    def run_ANDI(self):
        self.push(self.pop() & self.pop())

    def run_ORI(self):
        self.push(self.pop() | self.pop())

    def run_GROW(self):
        self.memory.extend(b'\x00'*self.pop())
        self.push(len(self.memory))

    def run_PEEKI(self):
        addr = self.pop()
        self.push(struct.unpack("<i", self.memory[addr:addr+4])[0])

    def run_PEEKF(self):
        addr = self.pop()
        self.push(struct.unpack("<d", self.memory[addr:addr+8])[0])

    def run_PEEKB(self):
        addr = self.pop()
        self.push(self.memory[addr])
                   
    def run_POKEI(self):
        value = self.pop()
        addr = self.pop()
        self.memory[addr:addr+4] = struct.pack("<i", value)

    def run_POKEF(self):
        value = self.pop()
        addr = self.pop()
        self.memory[addr:addr+8] = struct.pack("<d", value)

    def run_POKEB(self):
        value = self.pop()
        addr = self.pop()
        self.memory[addr] = value

    def run_IF(self):
        if not self.pop():
            self.pc = self.control[self.pc]

    def run_ELSE(self):
        self.pc = self.control[self.pc]

    def run_ENDIF(self):
        pass

    def run_LOOP(self):
        pass

    def run_CBREAK(self):
        if self.pop():
            self.pc = self.control[self.pc]

    def run_ENDLOOP(self):
        self.pc = self.control[self.pc]

    def run_CALL(self, name):
        self.execute(name)

    def run_RETURN(self):
        self.pc = len(self.code)

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def main():
    import sys
    from .ircode import compile_ircode
    from .errors import errors_reported

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m wabbit.interp filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    module = compile_ircode(source)
    if module:
        interpreter = Interpreter()
        has_main = False
        for func in module.functions:
            argnames = [p[0] for p in func.parameters]
            interpreter.add_function(func.name, argnames, func.code)
            if func.name == 'main':
                has_main = True

        interpreter.execute('__init')
        if has_main:
            interpreter.execute('main')


if __name__ == '__main__':
    main()






        
        
        
