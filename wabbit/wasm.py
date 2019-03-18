# wasm.py
# 
# CAUTION:  Don't even work here until you've done Exercise 5.

import struct

'''
Web Assembly Encoder
====================

This file directly encodes Wabbit IR code into a Wasm executable file
with no secondary tools.  Doing this is relatively straightforward,
but involves a lot of low-level binary data encoding.   The definitive
reference for this encoding is the Wasm specification at 
https://webassembly.github.io/spec/.   That document is not the easiest
read so a high-level description is given here.  

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
    data = value.encode('utf-8')
    return encode_vector(list(data[i:i+1] for i in range(len(data))))

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
Section 5     | Memory specifier             |
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
    pass     # YOU MUST IMPLEMENT

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

# You must implement signature encoding (see Exercise 5)

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

# You must implement import encoding (see Exercise 5)

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

# You must implement function declaration encoding (see Exercise 5)

'''
Memory (Section 5)
------------------
Section 5 encodes the memory section.  It's a vector of
memory specifiers, each have a minimum and optional maximum
like this:

   memtype ::=  \x00 <u32:min>
            |   \x01 <u32:min> <u32:max>

The min and max are specified in pages.  Each page is 64Kb. 
At this time, only one memory section can be specified.
'''

# You must implement memory section (if needed)

'''
Module Exports (Section 7)
--------------------------
For functions to be visible from JS, they need to be exported.
The exports section can export functions, globals, tables, and memory.
For our purposes, we are only interested in functions.  

Each function export is a record of the following form:

    <name:utf8> b'\x00' <funcidx:u32>

Each memory export is a record of the following form:

    <name:utf8> b'\x02' <memoryidx:u32>

The contents of section 7 are encoded as a vector of export records.
'''

# You implement

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

# You implement (see Exercise 5)


# Mapping of Wabbit types to Wasm types
typemap = {
    'int': i32,
    'float': f64,
    'char': i32,
}

class WasmWabbit:
    '''
    Low-level instruction encoder.
    '''
    def __init__(self):
        # Type signature table.  Each unique function type signature
        # should go here.  The default values shown are for the
        # imported "print" functions needed for output. For section 1.
        self.typesigs = [
            encode_type_signature([i32], []),   
            encode_type_signature([f64], []),
            ]

        # Function imports.  Any functionality needed from the Javascript
        # environment needs to go here.  The third number refers to a type
        # signature in the table above.  Note: You'll need to figure out
        # how to encode these.  For section 2.
        self.imports = [
            encode_function_import('wabbit', '_printi', 0),
            encode_function_import('wabbit', '_printf', 1),
            encode_function_import('wabbit', '_printb', 0)
            ]

        # Mapping of function names to funcidx integers.  This mapping
        # is for convenience. If you want to call a function, look up
        # its index here. The functions listed in imports always go first.
        self.functions = { }

        # List of function typesigs for native Wasm functions.  This
        # is list of typeidx integers.  The integers correspond to 
        # entries in self.typesigs.  (for section 3)
        self.func_defns = []

        # List of function exports (for section 7)
        self.exports = [ ]

        # List of function code definitions (for section 10)
        self.func_code = [ ]
    
    def generate_function_code(self, name, argtypes, rettypes, ircode):
        '''
        Generate Wasm code for a function.
        '''
        # See Exercise 5.

        self.code = bytearray()
        self.locals = { }
        self.localtypes = []

    # Interpreter opcodes
    def emit_CONSTI(self, value):
        self.code.extend([b'\x41', encode_signed(value)])

    def emit_CONSTF(self, value):
        pass    # You implement

    def emit_ADDI(self):
        self.code.append(b'\x6a')

    def emit_ADDF(self):
        pass    # You implement

    def emit_SUBI(self):
        pass    # You implement

    def emit_SUBF(self):
        pass    # You implement

    def emit_MULI(self):
        pass    # You implement
        
    def emit_MULF(self):
        pass    # You implement

    def emit_DIVI(self):
        pass    # You implement

    def emit_DIVF(self):
        pass    # You implement

    def emit_PRINTI(self):
        self.code.extend([b'\x10', encode_unsigned(self.functions['_printi'])])

    def emit_PRINTF(self):
        pass    # You implement

    def emit_PRINTB(self):
        pass    # You implement

    def emit_VARI(self, name):
        self.locals[name] = len(self.localtypes)
        self.localtypes.append(i32)

    def emit_VARF(self, name):
        pass    # You implement
        
    def emit_LOAD(self, name):
        self.code.extend([b'\x20', encode_unsigned(self.locals[name])])

    def emit_STORE(self, name):
        self.code.extend([b'\x21', encode_unsigned(self.locals[name])])

    def emit_ITOF(self):
        self.code.append(b'\xb7')   # f64.convert_i32_s

    def emit_FTOI(self):
        pass    # You implement

    def emit_GROW(self):
        pass    # You implement
        
    def emit_PEEKI(self):
        pass    # You implement

    def emit_PEEKF(self):
        pass    # You implement

    def emit_PEEKB(self):
        pass    # You implement

    def emit_POKEI(self):
        pass    # You implement

    def emit_POKEF(self):
        pass    # You implement

    def emit_POKEB(self):
        pass    # You implement

    # ---- Write the Wasm module
    def encode(self):
        # Return a byte-string representing the encoded module.
        # See Exercise 5.

        # Section 1: Type signatures
        # Section 2: Imports
        # Section 3: Function defns
        # Section 5: Memory
        # Section 7: Exports
        # Section 10: Functions

        return encoded_module

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def main():
    import sys
    from .ircode import compile_ircode
    from .errors import errors_reported

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m wabbit.wasm filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)
    if code:
        encoder = WasmWabbit()
        encoder.generate_function_code("main", [], [], code)
        return encoder

if __name__ == '__main__':
    encoder = main()
    with open('out.wasm', 'wb') as f:
        f.write(encoder.encode())
