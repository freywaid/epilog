"""
"""
import contextlib
import inspect
import itertools


def asargs(items):
    return ', '.join(repr(i) for i in items)


def expand_opexprs(toks):
    starts = ( max(i-1, 0) for i in range(0, len(toks), 3) )
    exprs = ( toks[s:s+3] for s in starts )
    return [ (op,(a,b)) for a,op,b in exprs ]


def quote_opexprs(toks):
    line = ( toks[s:s+2] for s in range(1, len(toks), 2) )
    return sum(( [str(op),repr(a)] for op,a in line ), start=[repr(toks[0])])


class SymTable(dict):
    def __init__(self, key=''):
        self.key = key
        self.count = 0
    def allocate(self, name, type):
        l = [name, self.count, self.key]
        if type:
            l.insert(0, type)
        n = '_'.join(str(i) for i in l)
        self.count += 1
        return n
    def var(self, name):
        return Var(self, name)
    def __call__(self, name):
        return self.var(name)

class Sym:
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return self.key


class Op:
    def __init__(self, s, loc, toks):
        self.s = s
        self.loc = loc
        self.toks = toks
    def __repr__(self):
        return f'{self.__class__.__name__}({asargs(self.toks)})'
    def __str__(self):
        return repr(self)


class Rule(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        t = toks[0]
        self.name = t[0]
        self.params = t[1]
        self.suite = [ i[0] for i in t[2] ]
    def decl(self):
        return f'{self.name}({asargs(self.params)})'
    def __repr__(self):
        indent = ' '*4
        return f'rule {self.decl()}:\n' + \
            '\n'.join(indent + repr(i) for i in self.suite)

class Var(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.name = toks[0]
    def __repr__(self):
        return self.name


class Group(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.group = toks[0]
    def __repr__(self):
        return f'({self.group})'


class List(Op):
    def __repr__(self):
        return f'[{asargs(self.toks)}]'


class Call(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.name = toks[0]
        self.args = toks[1:]
    def __repr__(self):
        return f'{self.name}({asargs(self.args)})'


class Slice(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        slice = ()
        while toks:
            item, *toks = toks
            if item == ':':
                item = None
            else:
                toks = toks[1:]
            slice += (item,)
        self.slice = slice
    def __repr__(self):
        s = ':'.join('' if i is None else repr(i) for i in self.slice)
        return f'[{s}]'


class Sliced(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.val = toks[0]
        self.slice = toks[1]
    def __repr__(self):
        return f'{self.val}{self.slice}'


class Not(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.val = toks[-1]
        self.not_count = len(toks) - 1
        self.notted = bool(self.not_count % 2)
    def __repr__(self):
        return 'not '*self.not_count + f'{self.val}'


class Factors(Op):
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.ops = toks[:-1]
        self.val = toks[-1]
    def __repr__(self):
        return f'{"".join(str(i) for i in self.ops)}{repr(self.val)}'



class OpExpr(Op):
    op = '<dunno>'
    def __init__(self, s, loc, toks):
        super().__init__(s, loc, toks)
        self.expanded = expand_opexprs(toks)
    def __repr__(self):
        return ' '.join(quote_opexprs(self.toks))


class BitOr(OpExpr):
    pass


class BitXor(OpExpr):
    pass


class BitAnd(OpExpr):
    pass


class And(OpExpr):
    pass


class Or(OpExpr):
    pass


class Unify(OpExpr):
    pass


class Power(OpExpr):
    pass


class Sums(OpExpr):
    pass


class MulDivs(OpExpr):
    pass


class Shifts(OpExpr):
    pass


class Comps(OpExpr):
    OPS = {
        '<': lambda a,b: a < b,
        '<=': lambda a,b: a <= b,
        '>': lambda a,b: a > b,
        '>=': lambda a,b: a >= b,
        '!=': lambda a,b: a != b,
        '==': lambda a,b: a == b,
        'in': lambda a,b: a in b,
        'not in': lambda a,b: a not in b,
        'is': lambda a,b: a is b,
        'is not': lambda a,b: a is not b,
    }
