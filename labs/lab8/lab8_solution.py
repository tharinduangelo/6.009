import sys
import builtins
import traceback as tb


class Symbol:
    def simplify(self):
        return self

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __rsub__(self, other):
        return Sub(other, self)

    def __rmul__(self, other):
        return Mul(other, self)

    def __rtruediv__(self, other):
        return Div(other, self)


def _is_zero(x):
    return isinstance(x, Num) and x.n == 0

def _is_one(x):
    return isinstance(x, Num) and x.n == 1


class Var(Symbol):
    prec = float('inf')

    def __init__(self, n):
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'

    def deriv(self, var):
        return Num(1 if var == self.name else 0)

    def eval(self, env):
        return env[self.name]


class Num(Symbol):
    prec = float('inf')

    def __init__(self, n):
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

    def deriv(self, var):
        return Num(0)

    def eval(self, env):
        return self.n


def _cast(i):
    if isinstance(i, int):
        return Num(i)
    if isinstance(i, str):
        return Var(i)
    if isinstance(i, Symbol):
        return i
    raise TypeError("%s can't be cast as a Symbol" % type(i).__name__)


class BinOp(Symbol):
    associative = True

    def __init__(self, left, right):
        self.left = _cast(left)
        self.right = _cast(right)

    def __str__(self):
        L = str(self.left)
        if self.left.prec < self.prec:
            L = '(%s)' % L
        R = str(self.right)
        if ((self.associative and self.right.prec < self.prec) or
                (not self.associative and self.right.prec <= self.prec)):
            R = '(%s)' % R
        return '%s %s %s' % (L, self.opstr, R)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self.left) + ', ' + repr(self.right) + ')'

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(self._combine_numbers(left.n, right.n))
        else:
            return self._simplify(left, right)

    def eval(self, env):
        l = self.left.eval(env)
        r = self.right.eval(env)
        return self._combine_numbers(l, r)


class Add(BinOp):
    prec = 0
    opstr = '+'

    def _combine_numbers(self, l, r):
        return l + r

    def deriv(self, var):
        return Add(self.left.deriv(var), self.right.deriv(var))

    def _simplify(self, l, r):
        if _is_zero(l):
            return r
        if _is_zero(r):
            return l
        return Add(l, r)


class Sub(BinOp):
    associative = False
    prec = 0
    opstr = '-'

    def _combine_numbers(self, l, r):
        return l - r

    def deriv(self, var):
        return Sub(self.left.deriv(var), self.right.deriv(var))

    def _simplify(self, l, r):
        if _is_zero(r):
            return l
        return Sub(l, r)


class Mul(BinOp):
    prec = 1
    opstr = '*'

    def _combine_numbers(self, l, r):
        return l * r

    def deriv(self, var):
        d_left = self.left.deriv(var)
        d_right = self.right.deriv(var)
        return (self.left * d_right) + (self.right * d_left)

    def _simplify(self, l, r):
        if _is_zero(r) or _is_zero(l):
            return Num(0)
        if _is_one(r):
            return l
        if _is_one(l):
            return r
        return Mul(l, r)


class Div(BinOp):
    associative = False
    prec = 1
    opstr = '/'

    def _combine_numbers(self, l, r):
        return l / r

    def deriv(self, var):
        d_left = self.left.deriv(var)
        d_right = self.right.deriv(var)
        num = (self.right * d_left) - (self.left * d_right)
        denom = self.right * self.right
        return Div(num, denom)

    def _simplify(self, l, r):
        if _is_one(r):
            return l
        if _is_zero(l):
            return Num(0)
        return Div(l, r)


def tokenize(x):
    return x.replace('(', ' ( ').replace(')', ' ) ').split()


_op_lookup = {
    '+': Add,
    '-': Sub,
    '*': Mul,
    '/': Div,
}

def parse(tokens):
    def parse_expression(index):
        tok = tokens[index]
        if tok.count('-') <= 1 and tok.replace('-', '').isdigit():
            return Num(int(tok)), index+1
        elif tok != '(':
            return Var(tok), index+1
        else:
            left, index = parse_expression(index+1)
            op = tokens[index]
            right, index = parse_expression(index+1)
            return _op_lookup[op](left, right), index+1 # +1 to skip trailing paren
    return parse_expression(0)[0]


def sym(expression):
    return parse(tokenize(expression))
