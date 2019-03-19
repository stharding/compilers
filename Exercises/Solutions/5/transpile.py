# transpile.py

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


class Transpiler:
    def __init__(self):
        self.outcode = 'def main():\n'
        self.stack = [ ]

    def translate(self, code):
        for op, *opargs in code:
            getattr(self, f'translate_{op}')(*opargs)
        self.outcode += '\nmain()\n'
        return self.outcode

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def translate_VARI(self, name):
        pass

    def translate_CONSTI(self, value):
        self.push(repr(value))

    def translate_STORE(self, name):
        self.outcode += f'    {name} = {self.pop()}\n'

    def translate_LOAD(self, name):
        self.push(name)

    def translate_ADDI(self):
        self.push(f'({self.pop()} + {self.pop()})')

    def translate_MULI(self):
        self.push(f'({self.pop()} * {self.pop()})')

    def translate_PRINTI(self):
        self.outcode += f'    print({self.pop()})\n'

trans = Transpiler()
print(trans.translate(code))
