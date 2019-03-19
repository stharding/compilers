# Exercise 0 - warmup.py
#
# A warmup exercise to illustrate some of the basic concepts of
# compilers.  It defines a very minimal virtual machine.  You are
# to write three programs based on this machine.   Follow instructions
# near the bottom of this file.
# ----------------------------------------------------------------------

# TinyVM.
#
# A tiny virtual machine.  The machine has 8 registers (R0,R1,...,R7)
# and understands the following 8 instructions--which are encoded as
# tuples.
#
#   ('ADD', 'Ra', 'Rb', 'Rd')     -> Rc = Ra + Rb
#   ('SUB', 'Ra', 'Rb', 'Rd')     -> Rc = Ra - Rb
#   ('MOV', value, 'Rd')          -> Rd = value
#   ('LD', 'Rs', 'Rd', offset)    -> Rd = MEMORY[Rs + offset]
#   ('ST', 'Rs', 'Rd', offset)    -> MEMORY[Rd + offset] = Rs
#   ('JMP', 'Rd', offset)         -> PC = Rd + offset
#   ('BRZ', 'Rt', offset)          -> if Rt == 0: PC = PC + offset
#   ('HALT,)                      -> Halts machine
#
# In the the above instructions 'Rx' means some register number such
# as R0, R1, etc.  Initially the machine initialzes R0,...,R6 to 0.
# R7 is initialized to last valid memory address.

class Halt(Exception):
    pass

class TinyVM(object):
    def run(self, memory):
        '''
        Run a program. memory is a Python list containing the program
        instructions and other data.  Upon startup, all registers
        are initialized to 0.  R7 is initialized with the highest valid
        memory address.
        '''
        self.pc = 0
        self.registers = { f'R{d}':0 for d in range(8) }
        self.memory = memory
        self.registers['R7'] = len(memory) - 1
        try:
            while True:
                op, *args = self.memory[self.pc]
                self.pc += 1
                getattr(self, op)(*args)
        except Halt:
            self.registers = { key: 0 for key in self.registers }
        return

    def ADD(self, ra, rb, rd):
        # print(self.registers)
        self.registers[rd] = self.registers[ra] + self.registers[rb]

    def SUB(self, ra, rb, rd):
        self.registers[rd] = self.registers[ra] - self.registers[rb]

    def MOV(self, value, rd):
        self.registers[rd] = value

    def LD(self, rs, rd, offset):
        self.registers[rd] = self.memory[self.registers[rs]+offset]

    def ST(self, rs, rd, offset):
        print(self.registers)
        self.memory[self.registers[rd]+offset] = self.registers[rs]

    def JMP(self, rd, offset):
        self.pc = self.registers[rd] + offset

    def BRZ(self, rt, offset):
        if not self.registers[rt]:
            self.pc += offset

    def HALT(self):
        raise Halt()


machine = TinyVM()

# ----------------------------------------------------------------------
# Problem 1:  Computers
#
# The CPU of a computer executes low-level instructions.  Using the
# TinyVM instruction set above, show how you would compute 2 + 3 - 4.

prog1 = [ # Instructions here
          ('MOV', 2, 'R1'),
          ('MOV', 3, 'R2'),
          ('ADD', 'R1', 'R2', 'R3'),
          ('MOV', 4, 'R4'),
          ('SUB', 'R3', 'R4', 'R5'),
          ('ST', 'R5', 'R7', 0),    # Save result. Replace 'RESULT' with a register
          ('HALT',),
          0            # Store the result here (note: R7 holds this address)
          ]

machine.run(prog1)
print('Program 1 Result:', prog1[-1], '(should be 1)')

# ----------------------------------------------------------------------
# Problem 2: Computation
#
# Write a TinyVM program that computes 23 * 37.  Note: The machine
# doesn't implement multiplication.  So, you need to figure out how
# to do it.

prog2 = [ # Instructions here
          ('MOV', 0, 'R6'),
          ('MOV', 1, 'R5'),
          ('MOV', 23, 'R1'),
          ('MOV', 23, 'R4'),
          ('MOV', 37, 'R2'),
          ('BRZ', 'R2', 5),
          ('ADD', 'R4', 'R1', 'R1'),
          ('SUB', 'R2', 'R5', 'R2'),
          ('JMP', 'R6', 5),
          ('ST', 'R1', 'R7', 0),
          ('HALT',),
          0           # Store result here
        ]

machine.run(prog2)
print('Program 2 Result:', prog2[-1], f'(Should be {23*37})')

# ----------------------------------------------------------------------
# Problem 3: Abstraction
#
# Write a Python function mul(x, y) that computes x * y on TinyVM.
# This function, should abstract details away--you're not supposed to
# worry about how it works.  Just call mul(x, y).

def mul(x, y):
    prog = [ # Instructions here
             # ...
             ('HALT',),
             x,      # Input value
             y,      # Input value
             0       # Result
    ]
    machine.run(prog)
    return prog[-1]

print(f'Problem 3: 51 * 53 = {mul(51, 53)}. Should be {51*53}')
