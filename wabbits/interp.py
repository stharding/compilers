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
        # Variable storage
        self.vars = { }

        # The operation stack
        self.stack = [ ]

        # Memory
        self.memory = bytearray()

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def execute(self, code):
        self.vars = { }
        for inst, *args in code:
            getattr(self, f'run_{inst}')(*args)
        
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

    def run_LOAD(self, name):
        self.push(self.vars[name])

    def run_STORE(self, name):
        self.vars[name] = self.pop()

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
    code = compile_ircode(source)
    if code:
        interpreter = Interpreter()
        interpreter.execute(code)

if __name__ == '__main__':
    main()






        
        
        
