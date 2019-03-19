# simple_interp.py

# Example program
#
#    var x int = 4;
#    var y int = 5;
#    var d int = x * x + y * y;
#    print d;
#

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

class Interpreter:
    def __init__(self):
        self.store = { }
        self.stack = [ ]
        self.pc = 0

    def run(self, code):
        self.pc = 0
        while self.pc < len(code):
            op, *opargs = code[self.pc]
            getattr(self, f'run_{op}')(*opargs)
            self.pc += 1

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def run_VARI(self, name):
        self.store[name] = None

    def run_CONSTI(self, value):
        self.push(value)

    def run_STORE(self, name):
        self.store[name] = self.pop()

    def run_LOAD(self, name):
        self.push(self.store[name])

    def run_ADDI(self):
        self.push(self.pop() + self.pop())

    def run_MULI(self):
        self.push(self.pop() * self.pop())

    def run_PRINTI(self):
        print(self.pop())

interp = Interpreter()
interp.run(code)
