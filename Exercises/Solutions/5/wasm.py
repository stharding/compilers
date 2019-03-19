import struct
import itertools

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

def encode_name(name):
    '''
    Encode a text name as a UTF-8 vector
    '''
    return encode_vector(name.encode('utf-8'))

def encode_section(sectnum, contents):
    return bytes([sectnum]) + encode_unsigned(len(contents)) + contents

i32 = b'\x7f'
f64 = b'\x7c'

class WasmEncoder:
    def __init__(self):
        # List of function objects created
        self.functions = [ ]
        self.typesigs = [ ]
        self.functypes = [ ] 
        self.exports = [ ]
        self.imports = [ ]

        # Import built-in runtime functions
        self._printi = self.import_function('runtime', '_printi', [i32], [])

    def import_function(self, module, name, argtypes, rettypes):
        # Make a type signature
        typesig = b'\x60' + encode_vector(argtypes) + encode_vector(rettypes)
        self.typesigs.append(typesig)
        typeidx = len(self.typesigs) - 1

        # Make an import record
        enc = encode_name(module) + encode_name(name) + b'\x00' + encode_unsigned(typeidx)
        self.imports.append(enc)
        funcidx = len(self.imports) - 1
        return funcidx

    def encode_function(self, name, argtypes, rettypes, code):

        # Create a type signature
        typesig = b'\x60' + encode_vector(argtypes) + encode_vector(rettypes)
        self.typesigs.append(typesig)
        typeidx = len(self.typesigs) - 1

        # Add the typeidx to the functypes list
        self.functypes.append(encode_unsigned(typeidx))
        funcidx = len(self.imports) + len(self.functypes) - 1

        # Add the funcidx to the exports list
        self.exports.append(encode_name(name) + b'\x00' + encode_unsigned(funcidx))

        # Now make the function instructions
        self.wcode = b''
        self.vars = { }
        self.vartypes = [ ]

        for op, *opargs in code:
            getattr(self, f'encode_{op}')(*opargs)
        self.wcode += b'\x0b'

        # Create the proper encoding of the entire function
        groups = []
        for ty, items in itertools.groupby(self.vartypes):
            groups.append((len(list(items)), ty))

        parts = [ encode_unsigned(count) + ty for count, ty in groups ]
        enc_locals = encode_vector(parts)
        func = enc_locals + self.wcode
        self.functions.append(encode_unsigned(len(func)) + func)

    def encode_module(self):
        module = b'\x00asm\x01\x00\x00\x00'
        module += encode_section(1, encode_vector(self.typesigs))
        module += encode_section(2, encode_vector(self.imports))
        module += encode_section(3, encode_vector(self.functypes))
        module += encode_section(7, encode_vector(self.exports))
        module += encode_section(10, encode_vector(self.functions))
        return module

    def encode_VARI(self, name):
        self.vars[name] = len(self.vars)
        self.vartypes.append(b'\x7f')

    def encode_CONSTI(self, value):
        self.wcode += b'\x41' + encode_signed(value)

    def encode_STORE(self, name):
        self.wcode += b'\x21' + encode_unsigned(self.vars[name])

    def encode_LOAD(self, name):
        self.wcode += b'\x20' + encode_unsigned(self.vars[name])

    def encode_ADDI(self):
        self.wcode += b'\x6a'

    def encode_MULI(self):
        self.wcode += b'\x6c'

    def encode_PRINTI(self):
        self.wcode += b'\x10' + encode_unsigned(self._printi)

encoder = WasmEncoder()
encoder.encode_function("main", [], [], code)
with open('out.wasm', 'wb') as file:
    file.write(encoder.encode_module())


