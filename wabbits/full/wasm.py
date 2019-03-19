# wasm.py

import struct
from typing import NamedTuple, List

'''
Web Assembly Encoder
====================

This file directly encodes Wabbit IR code into a Wasm executable file
with no secondary tools.  Doing this is relatively straightforward,
but involves a lot of low-level binary data encoding.   The definitive
reference for this encoding is the Wasm specification at 
https://webassembly.github.io/spec/.   That document is not the easiest
read so a high-level description is given here.  

The code you need to write is not terribly difficult, but there are
a lot of moving parts. So, read through this first.

Primitives
----------
There are four primitive data types used in the encoding:

  unsigned  - Unsigned integer. Encoded as LEB128.
  signed    - Signed integer. Encoded as LEB128.
  f64       - 64-bit float. Encoded as little-endian double precision.
  byte      - An 8-bit byte. Encoded as is.

The following functions are used for these encodings:
'''

def encode_unsigned(value):
    '''
    Produce an LEB128 encoded unsigned integer.
    '''
    parts = []
    for i in range((value.bit_length() // 7)+1):
        parts.append((value & 0x7f) | 0x80)
        value >>= 7
    if value:
        parts.append(value)
    if not parts:
        parts.append(0)
    parts[-1] &= 0x7f
    return bytes(parts)

def encode_signed(value):
    '''
    Produce a LEB128 encoded signed integer.
    '''
    if value >= 0:
        return encode_unsigned(value)
    else:
        value = (1 << (value.bit_length() + (7 - value.bit_length() % 7))) + value
        return encode_unsigned(value)

def encode_f64(value):
    '''
    Encode a 64-bit float point as little endian
    '''
    return struct.pack('<d', value)

'''
Vectors
-------
Sometimes data is encoded into a vector.  A vector consists
of a u32 size followed by the encoded elements.  One common
type is a text name.  This is encoded as a u32 size followed
by the raw bytes of its UTF-8 encoding:

   name : <u32:size><utf8_bytes>

Functions for vector and name encoding have been given below.
'''
def encode_vector(items):
    '''
    A size-prefixed collection of objects.  If items is already
    bytes, it is prepended by a length and returned.  If items
    is a list of byte-strings, the length of the list is prepended
    to byte-string formed by concatenating all of the items.
    '''
    if isinstance(items, bytes):
        return encode_unsigned(len(items)) + items
    else:
        return encode_unsigned(len(items)) + b''.join(items)

def encode_name(value):
    '''
    Encode a text name as a UTF-8 vector
    '''
    return encode_vector(value.encode('utf-8'))

'''
Wasm File Structure
-------------------
A basic .wasm file is encoded into sections.  The following sections
are pertinent to our project.

              |------------------------------|
Magic/Version | b'\x00asm\x01\x00\x00\x00'   |
              |------------------------------|
Section 1     | Function Type Signatures     |
              |------------------------------|
Section 2     | Module Imports               |
              |------------------------------|
Section 3     | Function declarations        |
              |------------------------------|
Section 7     | Module Exports               |
              |------------------------------|
Section 10    | Function code                |
              |------------------------------|

Each section is encoded as a single byte section number followed by
a u32-encoded section length and the raw contents.  The
function encode_section() below can be used to encode a section.
'''

def encode_module(sections):
    return b'\x00asm\x01\x00\x00\x00' + b''.join(section.encode() for section in sections)

class ModuleSection(NamedTuple):
    number: int
    contents: bytes

    def encode(self):
        return bytes([self.number]) + encode_unsigned(len(self.contents)) + self.contents

'''
Function Type Signatures  (Section 1)
-------------------------------------
A type signature describes the input argument types and return value
type of a function.  Wasm uses the following codes to encode value types:

    valuetype := 
          b'\x7f' => i32
          b'\x7e' => i64
          b'\x7d' => f32
          b'\x7c' => f64

A function signature consists of two vectors (argtypes, rettypes)
describing input types and output types.  Both argtypes and rettypes
may be an empty list to indicate no inputs or no return value respectively.
For example, a function like this:

     func add(x int, y int) int {
         return x + y;
     }

Has a signature of ([i32, i32], [i32]).  A single type signature is
encoded as follows:

     typesig ::= b'\x60' + vector<valuetype> + vector<valuetype>

For the signature above, the raw encoding looks like this:

     b'\x60\x02\x7f\x7f\x01\x7f'

Section 1 of the Wasm file consists of a vector of unique type
signatures.  It is only necessary to encode the *unique* signatures.
Suppose you had a file with 4 functions in it like this:

     func add(x int, y int) int { ... }
     func sub(x int, y int) int { ... }
     func mul(x int, y int) int { ... }
     func fact(n int) int { ... }

The signature vector would only contain two entries

   typeidx signature
   ------- -------------------
   0       [[i32, i32], [i32]]
   1       [[i32], [i32]]

The first entry would be used for the first three functions (this
is described below).  Note, the contents of section 1 for these
signatures would look like this:
    
    b'\x02\x60\x02\x7f\x7f\x01\x7f\x60\x01\x7f\x01\x7f'
      ^^^^ ^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^
        |           |                      |
        |           |                      +--> [[i32], [i32]]
        |           |              
        |           +---> [[i32, i32], [i32]]
        |
        +---> # of signatures (2)

To encode section 1, you take these contents and use the
encode_section() function above.
'''

# Value types
i32 = b'\x7f'      # Encoding of the i32 type
f64 = b'\x7c'      # Encoding of the f64 type

class TypeSig(NamedTuple):
    args: List[bytes]        # Must contain value types
    returns: List[bytes]     # Must contain value types

    def encode(self):
        return b'\x60' + encode_vector(self.args) + encode_vector(self.returns)

def encode_all_signatures(sigs):
    return encode_vector([sig.encode() for sig in sigs])

'''
Imports (Section 2)
-------------------
A Wasm module is allowed to import definitions for use.  This is
very similar to the idea of module imports in Python.  Wasm allows
the import of functions, globals, tables, and memory.  For the
project, we are only concerned with functions. 

To import a function, you first need to know its type signature.  This
type signature must be encoded in the "Type Signature" section 1
described above.  You also need to know the index into the type table
(typeidx).  For example, if the imported function had a signature of
([i32], [i32]), it would have typeidx=1 according to the table above.

Each function import is encoded as a record of the following form:

    importrec ::= <modulename:utf8> <name:utf8> b'\x00' <typeidx:u32>

The contents of section 2 are encoded as a vector of import records.

Important note: imported functions are labeled by funcidx integers
starting at 0.  funcidx=0 is the first imported function, funcidx=1
is the second imported function, and so forth.  These funcidx
labels are important when making function calls in the generated machine
code.
'''

class FunctionImport(NamedTuple):
    module: str
    name: str
    typeidx: int

    def encode(self):
        return encode_name(self.module) + encode_name(self.name) + b'\x00' + encode_unsigned(self.typeidx)        

def encode_all_imports(imports):
    return encode_vector([imp.encode() for imp in imports])

'''
Function Declarations (Section 3)
---------------------------------
Section 3 of a Wasm module is a vector of type signatures
corresponding to the functions defined in the module (not imports).  
It is vector typeidx integers. For example, if you had these
functions:

     func add(x int, y int) int { ... }
     func sub(x int, y int) int { ... }
     func mul(x int, y int) int { ... }
     func fact(n int) int { ... }

Section 1 would have these type signatures:

   typeidx signature
   ------- -------------------
   0       [[i32, i32], [i32]]
   1       [[i32], [i32]]

Sction 3 would be a vector that looks like this:

   [0, 0, 0, 1]

Functions are identified by funcidx integers.  For functions
defined inside the module (not imported), numbering starts
*after* all of the functions in the import section.  For
example, if there were two imported functions, the four
functions above would have funcidx values of [2, 3, 4, 5].
These numbers are used in function calls and exports.
'''

def encode_function_declarations(typeidxs):
    '''
    Encode the contents of section 3.  It's a vector of
    integer typeidx indices
    '''
    return encode_vector([encode_unsigned(idx) for idx in typeidxs])

'''
Memory (Section 5)
------------------
Section 5 encodes memory the requirements.  It's a vector of
memory specifiers, each have a minimum and optional maximum
like this:

   memtype ::=  \x00 <u32:min>
            |   \x01 <u32:min> <u32:max>

The min and max are specified in pages.  Each page is 64Kb. 
At this time, only one memory section can be specified.
'''

class MemoryType(NamedTuple):
    min: int
    max: int

    def encode(self):
        if self.max is None:
            return b'\x00' + encode_unsigned(self.min)
        else:
            return b'\x01' + encode_unsigned(self.min) + encode_unsigned(self.max)

'''
Globals (Section 6)
-------------------
The globals section is for global variables. 
'''

class GlobalVar(NamedTuple):
    valtype: bytes
    expr : bytes
    def encode(self):
        return self.valtype + b'\x01' + self.expr

def encode_global_declarations(globals):
    return encode_vector([g.encode() for g in globals])


'''
Module Exports (Section 7)
--------------------------
For functions to be visible from JS, they need to be exported.
The exports section can export functions, globals, tables, and memory.
For our purposes, we are only interested in functions.  
Each function export is a record of the following form:

    <name:utf8> b'\x00' <funcidx:u32>

The contents of section 7 are encoded as a vector of export records.
'''

class FunctionExport(NamedTuple):
    name: str
    funcidx: int

    def encode(self):
        return encode_name(self.name) + b'\x00' + encode_unsigned(self.funcidx)

class MemoryExport(NamedTuple):
    name: str
    memidx: int

    def encode(self):
        return encode_name(self.name) + b'\x02' + encode_unsigned(self.memidx)

def encode_all_exports(exports):
    return encode_vector([exp.encode() for exp in exports])

'''
Function Code (Section 10)
--------------------------
The raw assembly code for various functions is contained in this
section.  The order and number of functions must exactly match
the number of entries in the Function Declaration Section 3.
The encoding of this part is a bit tricky because there are
multiple parts, nested within each other.

The section is encoded as a vector of code records. A
code record represents the raw encoding of a function 
and has the following form:

    code ::= <u32:size> <func>

The size is the size (in bytes) of the function function
that follows.

The associated <func> includes declarations of local variables
<locals> and the raw instructions <expr>.

    func ::= <vector(locals)> <expr>

The <locals> part is a vector of local variable record. A local
variable record encodes a set of local variables of the *same* type.
It's encoded as:

    locals ::= <u32:count> <valuetype>

This is potentially very confusing, but here's a concrete
example. Suppose you had a function like this:

    func f(x int, y int) int {
         var a int;
         var b int;
         var c float;
         ...
    }

The local variables to this are "a", "b", and "c".  These locals
are represented as follows:

    [ (2, i32), (1, f64) ]
      ^^^^^^^^  ^^^^^^^^
         |         + 1 local of type 'f64'
         |
      2 locals of type 'i32'

When fully encoded, the locals would look like this:

      b'\x02\x02\x7f\x01\x7c'
        ^^^^ ^^^^^^^ ^^^^^^^^
         |      |        |
         |      |        +-> 1 f64 local
         |      |  
         |      +-> 2 i32 locals
         |
         +-> 2 entries

The <expr> part of a function is the raw Wasm instructions for the
function.  These appear immediately after the locals.  The
instructions must be terminated by a b'\x0b' opcode to end the block.
'''

def encode_local(count, valuetype):
    '''
    Encode a single group of local variables of the same type
    '''
    return encode_unsigned(count) + valuetype

def encode_all_locals(locals):
    '''
    Encode all local variables. locals should be a list of
    of value types such as [i32, i32, f64, i32, f64, f64].
    This list will be subdivided into groups and passed
    to encode_local()

        encode_local(2, i32)
        encode_local(1, f64)
        encode_local(1, i32)
        encode_local(2, f64)
    '''
    from itertools import groupby
    parts = []
    for valuetype, group in groupby(locals):
        parts.append(encode_local(len(list(group)), valuetype))
    return encode_vector(parts)

class FunctionCode(NamedTuple):
    locals: List[bytes]
    expr: List[bytes]

    def encode(self):
        funcenc = encode_all_locals(self.locals) + b''.join(self.expr)
        return encode_unsigned(len(funcenc)) + funcenc

def encode_functions(funcs):
    '''
    Encode the code for all functions
    '''
    return encode_vector([f.encode() for f in funcs])

PAGESIZE = 64*1024

class WasmWabbit:
    '''
    Low-level instruction encoder.
    '''
    def __init__(self):
        # Type signature table.  Each unique function type signature
        # should go here.  The default values shown are for the
        # imported "print" functions needed for output.
        self.typesigs = [
            TypeSig([i32], []),   
            TypeSig([f64], []),
            ]

        # Function imports.  Any functionality needed from the Javascript
        # environment needs to go here.  The third number refers to a type
        # signature in the table above.
        self.imports = [
            FunctionImport('wabbit', '_printi', 0),
            FunctionImport('wabbit', '_printf', 1),
            FunctionImport('wabbit', '_printb', 0)
            ]

        # Mapping of function names to funcidx integers.  This mapping
        # is for convenience. If you want to call a function, look up
        # its index here. The functions listed in imports always go first.
        self.functions = { im[1]:n for n,im in enumerate(self.imports) }

        # List of function typesigs for native Wasm functions.  This
        # is list of typeidx integers.  The integers correspond to 
        # entries in self.typesigs.  
        self.func_defns = []

        # List of FunctionExport objects.  This contains FunctionExport
        # entries of the form FunctionExport(name, funcidx) where name
        # is the name of the function and funcidx is an index corresponding
        # to an entries in self.func_defns + len(self.imports)
        self.exports = [ ]

        # List of FunctionCode objects of the form FunctionCode(locals, expr).
        # locals is a list of local variable types such as [i32, i32, f64, i32, f64].
        # expr is a list of byte fragments forming the actual opcodes.
        self.func_code = [ ]

        # Global declarations. Mapping of global names to global indices
        self.globals = { }

        # List of global declarations
        self.global_defns = []
    
    def import_function(self, name, argtypes, returns):
        sig = TypeSig(argtypes, returns)
        if sig in self.typesigs:
            typeidx = self.typesigs.index(sig)
        else:
            typeidx = len(self.typesigs)
            self.typesigs.append(sig)
            
        funcidx = len(self.imports)
        self.functions[name] = funcidx
        self.imports.append(FunctionImport('wabbit', name, typeidx))

    def declare_function(self, name, argtypes, returns):
        sig = TypeSig(argtypes, returns)
        if sig in self.typesigs:
            typeidx = self.typesigs.index(sig)
        else:
            typeidx = len(self.typesigs)
            self.typesigs.append(sig)

        # Add a function to the function declarations section
        funcidx = len(self.imports) + len(self.func_defns)
        self.func_defns.append(typeidx)
        self.functions[name] = funcidx
        self.func_code.append(None)     # Placeholder
        return funcidx

    def generate_function_code(self, name, argnames, ircode):
        '''
        Generate Wasm code for a function.  name is the name of the
        function. argnames are the argument names and ircode is the code.
        The function must already be declared using declare function.
        '''
        funcidx = self.functions[name]
        typesig = self.typesigs[self.func_defns[funcidx-len(self.imports)]]
        argtypes = typesig.args
        
        # Reset some variables used during code generation
        self.code = [ ]

        # Set up localtypes and local variables
        self.localtypes = [ ]
        self.locals = { }
        
        # Add arguments to locals
        for argname, argtype in zip(argnames, argtypes):
            self.locals[argname] = len(self.localtypes)
            self.localtypes.append(argtype)

        # Generate the code
        for inst, *opargs in ircode:
            getattr(self, f'emit_{inst}')(*opargs)
            
        # Make sure the code is properly terminated
        self.code.append(b'\x0b')

        funccode = FunctionCode(self.localtypes[len(argtypes):], self.code)
        self.func_code[funcidx - len(self.imports)] = funccode

        # Add an entry to module exports
        self.exports.append(FunctionExport(name, funcidx))

    # Interpreter opcodes
    def emit_CONSTI(self, value):
        self.code.extend([b'\x41', encode_signed(value)])

    def emit_CONSTF(self, value):
        self.code.extend([b'\x44', encode_f64(value)])

    def emit_ADDI(self):
        self.code.append(b'\x6a')

    def emit_ADDF(self):
        self.code.append(b'\xa0')

    def emit_SUBI(self):
        self.code.append(b'\x6b')

    def emit_SUBF(self):
        self.code.append(b'\xa1')

    def emit_MULI(self):
        self.code.append(b'\x6c')
        
    def emit_MULF(self):
        self.code.append(b'\xa2')

    def emit_DIVI(self):
        self.code.append(b'\x6d')

    def emit_DIVF(self):
        self.code.append(b'\xa3')

    def emit_LEI(self):
        self.code.append(b'\x4c')

    def emit_LEF(self):
        self.code.append(b'\x65')

    def emit_LTI(self):
        self.code.append(b'\x48')

    def emit_LTF(self):
        self.code.append(b'\x63')

    def emit_GEI(self):
        self.code.append(b'\x4e')

    def emit_GEF(self):
        self.code.append(b'\x66')

    def emit_GTI(self):
        self.code.append(b'\x4a')

    def emit_GTF(self):
        self.code.append(b'\x64')

    def emit_EQI(self):
        self.code.append(b'\x46')

    def emit_EQF(self):
        self.code.append(b'\x61')

    def emit_NEI(self):
        self.code.append(b'\x47')

    def emit_NEF(self):
        self.code.append(b'\x62')

    def emit_ANDI(self):
        self.code.append(b'\x71')

    def emit_ORI(self):
        self.code.append(b'\x72')

    def emit_PRINTI(self):
        self.code.extend([b'\x10', encode_unsigned(self.functions['_printi'])])

    def emit_PRINTF(self):
        self.code.extend([b'\x10', encode_unsigned(self.functions['_printf'])])

    def emit_PRINTB(self):
        self.code.extend([b'\x10', encode_unsigned(self.functions['_printb'])])

    def emit_VARI(self, name):
        self.locals[name] = len(self.localtypes)
        self.localtypes.append(i32)

    def emit_VARF(self, name):
        self.locals[name] = len(self.localtypes)
        self.localtypes.append(f64)

    def emit_GLOBALI(self, name):
        self.globals[name] = len(self.global_defns)
        self.global_defns.append(GlobalVar(i32, b'\x41'+encode_signed(0)+b'\x0b'))

    def emit_GLOBALF(self, name):
        self.globals[name] = len(self.global_defns)
        self.global_defns.append(GlobalVar(f64, b'\x44'+encode_f64(0.0)+b'\x0b'))
        
    def emit_LOAD(self, name):
        if name in self.locals:
            self.code.extend([b'\x20', encode_unsigned(self.locals[name])])
        else:
            self.code.extend([b'\x23', encode_unsigned(self.globals[name])])

    def emit_STORE(self, name):
        if name in self.locals:
            self.code.extend([b'\x21', encode_unsigned(self.locals[name])])
        else:
            self.code.extend([b'\x24', encode_unsigned(self.globals[name])])

    def emit_ITOF(self):
        self.code.append(b'\xb7')   # f64.convert_i32_s

    def emit_FTOI(self):
        self.code.append(b'\xaa')   # i32.trunc_f64_s

    def emit_GROW(self):
        self.emit_CONSTI(PAGESIZE-1)
        self.emit_ADDI()
        self.emit_CONSTI(PAGESIZE)
        self.emit_DIVI()
        self.code.append(b'\x40\x00')
        self.code.append(b'\x1a')
        self.code.append(b'\x3f\x00')
        self.emit_CONSTI(PAGESIZE)
        self.emit_MULI()
        
    def emit_PEEKI(self):
        self.code.append(b'\x28\x00\x00')

    def emit_PEEKF(self):
        self.code.append(b'\x2b\x00\x00')

    def emit_PEEKB(self):
        self.code.append(b'\x2d\x00\x00')

    def emit_POKEI(self):
        self.code.append(b'\x36\x00\x00')

    def emit_POKEF(self):
        self.code.append(b'\x39\x00\x00')

    def emit_POKEB(self):
        self.code.append(b'\x3a\x00\x00')

    def emit_IF(self):
        self.code.append(b'\x04\x40')
        
    def emit_ELSE(self):
        self.code.append(b'\x05')

    def emit_ENDIF(self):
        self.code.append(b'\x0b')

    def emit_CBREAK(self):
        self.code.append(b'\x0d\x01')

    def emit_ENDLOOP(self):
        self.code.append(b'\x0c\x00')
        self.code.append(b'\x0b')
        self.code.append(b'\x0b')

    def emit_LOOP(self):
        self.code.append(b'\x02\x40')
        self.code.append(b'\x03\x40')

    def emit_CALL(self, name):
        funcidx = self.functions[name]
        self.code.append(b'\x10' + encode_unsigned(funcidx))

    def emit_RETURN(self):
        self.code.append(b'\x0f')

    # ---- Write the Wasm module
    def encode(self):
        self.exports.append(MemoryExport('memory', 0))

        sections = []
        # Section 1: Type signatures
        sections.append(ModuleSection(1, encode_all_signatures(self.typesigs)))
        # Section 2: Imports
        sections.append(ModuleSection(2, encode_all_imports(self.imports)))
        # Section 3: Function defns
        sections.append(ModuleSection(3, encode_function_declarations(self.func_defns)))

        # Section 5: Memory
        sections.append(ModuleSection(5, encode_vector([MemoryType(1,None).encode()])))
        
        # Section 6: Globals
        sections.append(ModuleSection(6, encode_global_declarations(self.global_defns)))

        # Section 7: Exports
        sections.append(ModuleSection(7, encode_all_exports(self.exports)))

        # Section 8: Start function
        sections.append(ModuleSection(8, encode_unsigned(self.functions['__init'])))

        # Section 10: Functions
        sections.append(ModuleSection(10, encode_functions(self.func_code)))

        return encode_module(sections)

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

# Mapping of Wabbit types to Wasm types
typemap = {
    'int': i32,
    'float': f64,
    'char': i32,
    'bool': i32
}

def main():
    import sys
    from .ircode import compile_ircode
    from .errors import errors_reported

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m wabbit.wasm filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    module = compile_ircode(source)
    if module:
        encoder = WasmWabbit()
        # Imports must be declared first
        for func in module.imports:
            args = [typemap[arg[1]] for arg in func.parameters]
            if func.rettype in typemap:
                rettype = [typemap[func.rettype]]
            else:
                rettype = []
            encoder.import_function(func.name, args, rettype)

        # Functions declared in advance
        has_main = False
        for func in module.functions:
            args = [typemap[arg[1]] for arg in func.parameters]
            if func.rettype in typemap:
                rettype = [typemap[func.rettype]]
            else:
                rettype = []
            encoder.declare_function(func.name, args, rettype)
            if func.name == 'main':
                has_main = True
                
        if not has_main:
            mainfunc = encoder.declare_function('main', [], [])

        # Code generated for functions last
        for func in module.functions:
            encoder.generate_function_code(func.name, [arg[0] for arg in func.parameters], func)

        if not has_main:
            encoder.generate_function_code('main', [], [])

        return encoder

if __name__ == '__main__':
    encoder = main()
    with open('out.wasm', 'wb') as f:
        f.write(encoder.encode())
