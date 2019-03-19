# simplelex.py

from sly import Lexer

class SimpleLexer(Lexer):
    # Token names
    tokens = { NUMBER, ID, IF, ELSE, WHILE, ASSIGN, PLUS, LPAREN, RPAREN, TIMES, NE, LE, GE, LT, GT }

    # Ignored characters
    ignore = ' \t'

    # Token regexs
    NUMBER = r'\d+'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['if'] = IF
    ID['else'] = ELSE
    ID['while'] = WHILE
    ASSIGN = r'='
    PLUS = r'\+'
    LPAREN = r'\('
    RPAREN = r'\)'
    TIMES = r'\*'
    NE = r'!='
    LE = r'<='
    GE = r'>='
    LT = r'<'
    GT = r'>'

    def error(self, t):
        print('Bad character %r' % t.value[0])
        self.index += 1

    @_(r'\n+')
    def ignore_newline(self,  t):
        self.lineno += t.value.count('\n')


# Example
# if __name__ == '__main__':
#     text = 'abc 123 $ cde 456'
#     lexer = SimpleLexer()
#     for tok in lexer.tokenize(text):
#         print(tok)

# if __name__ == '__main__':
#     text = 'a = 3 + (4 * 5)'
#     lexer = SimpleLexer()
#     for tok in lexer.tokenize(text):
#         print(tok)

if __name__ == '__main__':
    text = '''
           a < b
           a <= b
           a > b
           a >= b
           a == b
           a != b
    '''
    lexer = SimpleLexer()
    for tok in lexer.tokenize(text):
        print(tok)
