"""
"""
import functools
import pyparsing as pp
from pyparsing import pyparsing_common as ppc
import elements as el


def flatten(toks):
    if len(toks) != 1:
        return
    r = toks[0]
    while isinstance(r, pp.ParseResults) and len(r) == 1:
        r = r[0]
    toks.clear()
    toks.append(r)


class onfound:
    def __init__(self, cls=None):
        self.cls = cls
    def __call__(self, *args):
        if not self.cls or len(args[2]) <= 1:
            return
        return self.cls(*args)


def opexpr(op, m, cls=None, rhs=None):
    rhs = m if rhs else m
    return (m + (op + rhs)[...]).setParseAction(onfound(cls))


L = pp.Literal
atleast = pp.OneOrMore
opt = pp.Optional

LPAREN = pp.Suppress('(')
RPAREN = pp.Suppress(')')
LBRACK = pp.Suppress('[')
RBRACK = pp.Suppress(']')
COLON = pp.Suppress(':')
NAME = pp.Word(pp.alphas + '_', pp.alphanums + '_')

string = pp.quotedString().setParseAction(pp.removeQuotes)
number = ppc.number()
comment = '#' + pp.restOfLine
var = NAME.copy().setParseAction(el.Var)

expr = pp.Forward()
stmt = pp.Forward()

stack = [1]
suite = pp.indentedBlock(expr, stack)

params = pp.Optional(pp.delimitedList(expr))

ruledecl = pp.Suppress('rule') + NAME + \
        pp.Group(LPAREN + params + RPAREN) + COLON
ruledef = pp.Group(ruledecl + suite).setParseAction(el.Rule)

grouped = (LPAREN + expr + RPAREN).setParseAction(el.Group)
listed = (LBRACK + params + RBRACK).setParseAction(el.List)
call = (NAME + LPAREN + params + RPAREN).setParseAction(el.Call)

sliceops = (opt(expr) + ':' + opt(expr) + opt(':' + expr)) | expr
slice = (LBRACK + sliceops + RBRACK).setParseAction(el.Slice)

compops = pp.oneOf('== != <= < >= >') | (L('is') + L('not')) | \
    (L('not') + L('in')) | L('in') | L('is')

atom = call | grouped | listed | string | number | var
primary = (atom + slice).setParseAction(el.Sliced) | atom
factor = (pp.oneOf('+ - ~')[...] + primary).setParseAction(onfound(el.Factors))
power = opexpr('**', factor, el.Power)
muldiv = opexpr(pp.oneOf('* / // % @'), power, el.MulDivs)
sum = opexpr(pp.oneOf('+ -'), muldiv, el.Sums)
shift = opexpr(pp.oneOf('<< >>'), sum, el.Shifts)
bitwise_and = opexpr('&', shift, el.BitAnd)
bitwise_xor = opexpr('^', bitwise_and, el.BitXor)
bitwise_or = opexpr('|', bitwise_xor, el.BitOr)
comparison = opexpr(compops, bitwise_or, el.Comps)
inversion = (pp.OneOrMore('not') + comparison).setParseAction(el.Not) | comparison
conjunction = opexpr('and', inversion, el.And)
disjunction = opexpr('or', conjunction, el.Or)
unify = opexpr('=', disjunction, el.Unify)

expr <<= unify

stmt <<= ruledef

body = pp.OneOrMore(stmt)
body.ignore(comment)

def parse(data):
    return body.parseString(data)

"""
    x('ye', 1)
    x(x) = ( y(7) = 9 ) = [1, 'hel']
    y = -~x[:1] * 7 + 9 << 8 and not 8
"""

test = \
"""
rule hello(there, 8):
    first = 'hello' = 9
    a or b = 9 < '8' >= 0 | '9'
    x('ye', 1)
    x(x) = ( y(7) = 9 ) = [1, 'hel']
    z = 8 ** 7
    x = ~-x
    y = ~y[:1] - (1 + 3 + x)
"""

if __name__ == '__main__':
    r = parse(test)
    for i in r:
        print(i, end='\n\n')
