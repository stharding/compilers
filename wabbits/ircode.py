# ircode.py
'''
Project 4
=========
In this project, you are going to turn the AST into a simple intermediate
machine code based on a stack architecture.  Make sure you read the 
machine description before beginning.  One nice thing about this project
is that you're now on the "happy path."  If your type checker works, then
the program is known to be "corect."  You don't really need to do any
kind of error checking here--just assume it's good.

A "Virtual" Machine
===================
An actual CPU typically consists of registers and a small set of basic
opcodes for performing mathematical calculations, loading/storing
values from memory, and basic control flow (branches, jumps, etc.).
For example, suppose you want to evaluate an operation like this:

    a = 2 + 3 * 4 - 5

On a CPU, it might be decomposed into low-level instructions like this:

    MOVI   #2, R1
    MOVI   #3, R2
    MOVI   #4, R3
    MULI   R2, R3, R4
    ADDI   R4, R1, R5
    MOVI   #5, R6
    SUBI   R5, R6, R7
    STORE  R7, "a"

Although you can make a compiler generate instructions directly for a
CPU, it is often simpler to target a higher-level of abstraction
instead.  One such abstraction is that of a stack machine.  For
example, to evaluate the above expression, you could generate
"instructions" like this instead:

    CONSTI 2      ; stack = [2]
    CONSTI 3      ; stack = [2, 3]
    CONSTI 4      ; stack = [2, 3, 4]
    MULI          ; stack = [2, 12]
    ADDI          ; stack = [14]
    CONSTI 5      ; stack = [14, 5]
    SUBI          ; stack = [9]
    STORE "a"     ; stack = []

Notice how there are no details about CPU registers or anything like
that here. It's much simpler (a lower-level module can figure out the
stack->register mapping later if it needs to).

CPUs usually have a small set of code datatypes such as integers and floats.
There are dedicated instructions for each type.  For example:

    ADDI   ; Integer add
    ADDF   ; Float add

With that in mind, here is a basic instruction set for our IR Code:

    ; Integer operations
    CONSTI  value            ; Push a integer literal
    VARI name                ; Declare an integer variable 
    ADDI                     ; Add top two items on stack
    SUBI                     ; Substract top two items on stack
    MULI                     ; Multiply top two items on stack
    DIVI                     ; Divide top two items on stack
    PRINTI                   ; Print top item on stack
    PEEKI                    ; Get integer from memory (address on stack)
    POKEI                    ; Put integer in memory (address, value on stack)
    ITOF                     ; Convert integer to float

    ; Floating point operations
    CONSTF value             ; Push a float literal
    VARF name                ; Declare an float variable 
    ADDF                     ; Add top two items on stack
    SUBF                     ; Substract top two items on stack
    MULF                     ; Multiply top two items on stack
    DIVF                     ; Divide top two items on stack
    PRINTF                   ; Print top item on stack
    PEEKF                    ; Get float from memory (address on stack)
    POKEF                    ; Put float in memory (address, value on stack) 
    FTOI                     ; Convert float to integer

    ; Byte-oriented operations (values are presented as integers)    
    PRINTB                   ; Print top item on stack
    PEEKB                    ; Get byte from memory (address on stack)
    POKEB                    ; Put byte in memory (address, value on stack)

    ; Variable load/store
    LOAD name                ; Load variable on stack (must be declared already)
    STORE name               ; Save variable from stack (must be declared already)

    ; Memory
    GROW nbytes              ; Increment memory size by nbytes (returns new size)

This instruction set will be expanded in later stages of the project
to include comparison operators and control flow.

One word about memory access... the PEEK and POKE instructions are
used to access raw memory addresses.  Both instructions require
a memory address to be on the stack first.  For the POKE instruction,
the address must be pushed first, followed by the value being stored.
The order is important and it's easy to mess it up.  So pay careful
attention to that.

Your Task
=========
Your task is as follows: Write a AST Visitor() class that takes a
program and flattens it to a sequence instructions represented as 
tuples of the form 

       (operation, operands, ...)

For example, the code at the top might look like this:

    code = [
       ('CONSTI', 2),
       ('CONSTI', 3),
       ('CONSTI', 4),
       ('MULI',),
       ('ADDI',),
       ('CONSTI', 5),
       ('SUBI',),
       ('STOREI', 'a'),
    ]

Testing
=======
The files Tests/irtest0-5.wb contain some input text along with
sample output. Work through each file to complete the project.
'''

from . import ast

# Operator to name mapping
opmap = {
    '+' : 'ADD',
    '-' : 'SUB',
    '*' : 'MUL',
    '/' : 'DIV',
}

class GenerateCode(ast.NodeVisitor):
    '''
    Node visitor class that creates stack machine instructions.
    '''
    def __init__(self):
        # The generated code
        self.code = []

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.code list.
    #
    # A few sample methods follow.  You may have to adjust depending
    # on the names and structure of your AST nodes.

    def visit_IntegerLiteral(self, node):
        self.code.append(('CONSTI', node.value))

    def visit_FloatLiteral(self, node):
        self.code.append(('CONSTF', node.value))

    def visit_CharLiteral(self, node):
        self.code.append(('CONSTI', ord(node.value)))

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if node.left.type == 'float':
            code = f'{opmap[node.op]}F'
        else:
            code = f'{opmap[node.op]}I'
        self.code.append((code,))
        
    def visit_UnaryOp(self, node):
        if node.op == '-' and node.operand.type == 'int':
            self.code.append(('CONSTI', 0))
            self.visit(node.operand)
            self.code.append(('SUBI',))
        elif node.op == '-' and node.operand.type == 'float':
            self.code.append(('CONSTF', 0.0))
            self.visit(node.operand)
            self.code.append(('SUBF',))
        else:
            self.visit(node.operand)

    # CHALLENGE:  Figure out some more sane way to refactor the code for
    # binary and unary operators

    def visit_PrintStatement(self, node):
        self.visit(node.value)
        if node.value.type == 'int':
            code = 'PRINTI'
        elif node.value.type == 'float':
            code = 'PRINTF'
        elif node.value.type == 'char':
            code = 'PRINTB'
        inst = (code,)
        self.code.append(inst)

    def emit_declaration(self, node):
        if node.type == 'float':
            declcode = f'VARF'
        else:
            declcode = f'VARI'

        self.code.append((declcode, node.name))
        if node.value:
            self.visit(node.value)
            self.code.append(('STORE', node.name))

    visit_ConstDeclaration = emit_declaration
    visit_VarDeclaration = emit_declaration

    def visit_SimpleLocation(self, node):
        if node.usage == 'read':
            self.code.append(('LOAD', node.name))
        elif node.usage == 'write':
            self.code.append(('STORE', node.name))

    def visit_ReadValue(self, node):
        self.visit(node.location)

    def visit_Assignment(self, node):
        if hasattr(node.location, 'addr'):
            self.visit(node.location.addr)
        self.visit(node.value)
        self.visit(node.location)

    def visit_TypeCast(self, node):
        target_type = node.type
        self.visit(node.value)
        src_type = node.value.type
        if target_type != 'float' and src_type == 'float':
            self.code.append(('FTOI',))
        if target_type == 'float' and src_type != 'float':
            self.code.append(('ITOF',))

    def visit_GrowMemory(self, node):
        self.visit(node.incr)
        self.code.append(('GROW',))

    def visit_MemoryLocation(self, node):
        # self.visit(node.addr)
        if node.type == 'int':
            ty = 'I'
        elif node.type == 'float':
            ty = 'F' 
        elif node.type == 'char':
            ty = 'B'
        if node.usage == 'write':
            op = f'POKE{ty}'
        else:
            self.visit(node.addr)
            op = f'PEEK{ty}'
        self.code.append((op,))

# ----------------------------------------------------------------------
#                          TESTING/MAIN PROGRAM
#
# Note: Some changes will be required in later projects.
# ----------------------------------------------------------------------

def compile_ircode(source):
    '''
    Generate intermediate code from source.
    '''
    from .parser import parse
    from .checker import check_program
    from .errors import errors_reported

    ast = parse(source)
    check_program(ast)

    # If no errors occurred, generate code
    if not errors_reported():
        gen = GenerateCode()
        gen.visit(ast)
        return gen.code
    else:
        return None

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m wabbit.ircode filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)
    if code:
        for instr in code:
            print(instr)

if __name__ == '__main__':
    main()
