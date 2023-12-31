#!/usr/bin/env python3
import os
import lab
import pickle
import pytest

from test_utils import safe_eval

TEST_DIRECTORY = os.path.dirname(__file__)


def symbol_rep(x):
    if isinstance(x, lab.BinOp):
        assert set(x.__dict__) == {'left', 'right'}, "%s instance should only contain 'left' and 'right' instance variables, not %r" % (x.__class__.__name__, set(x.__dict__))
        if isinstance(x, (lab.Add, lab.Mul)):  # commutative operations
            op_rep = frozenset
        elif isinstance(x, (lab.Sub, lab.Div)):
            op_rep = tuple
        else:
            raise NotImplementedError('Expected symbolic expression, got %s' % x.__class__.__name__)
        return (x.__class__.__name__, op_rep(symbol_rep(i) for i in (x.left, x.right)))
    elif isinstance(x, lab.Num):
        return ('Num', x.n)
    elif isinstance(x, lab.Var):
        return ('Var', x.name)
    else:
        raise NotImplementedError('Expected symbolic expression, got %s' % x.__class__.__name__)


# read in expected result
def read_expected(fname):
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', fname), 'r') as f:
        return safe_eval(f.read())


def test_combinations():
    result = 0 + lab.Var('x')
    expected = ('Add', frozenset({('Num', 0), ('Var', 'x')}))
    assert symbol_rep(result) == expected

    result = lab.Var('x') + 0
    expected = ('Add', frozenset({('Num', 0), ('Var', 'x')}))
    assert symbol_rep(result) == expected

    result = 0 + (lab.Var('y') * 2)
    expected = ('Add', frozenset({('Num', 0), ('Mul', frozenset({('Var', 'y'), ('Num', 2)}))}))
    assert symbol_rep(result) == expected

    result = ('z' * lab.Num(3)) + 0
    expected = ('Add', frozenset({('Mul', frozenset({('Num', 3), ('Var', 'z')})), ('Num', 0)}))
    assert symbol_rep(result) == expected

    result = (lab.Num(0) + 'x') * 'z'
    expected = ('Mul', frozenset({('Add', frozenset({('Num', 0), ('Var', 'x')})), ('Var', 'z')}))
    assert symbol_rep(result) == expected

    result = ((0 * lab.Var('y')) + lab.Var('x'))
    expected = ('Add', frozenset({('Var', 'x'), ('Mul', frozenset({('Var', 'y'), ('Num', 0)}))}))
    assert symbol_rep(result) == expected

    result = ('x' + (lab.Num(2)-2))
    expected = ('Add', frozenset({('Var', 'x'), ('Sub', (('Num', 2), ('Num', 2)))}))
    assert symbol_rep(result) == expected

    result = 20 + lab.Num(101) * (1 * lab.Var('z'))
    expected = ('Add', frozenset({('Mul', frozenset({('Num', 101), ('Mul', frozenset({('Var', 'z'), ('Num', 1)}))})), ('Num', 20)}))
    assert symbol_rep(result) == expected

    assert symbol_rep(lab.Num(1) + 2) == symbol_rep(1 + lab.Num(2))
    assert symbol_rep(lab.Num(1) * 2) == symbol_rep(1 * lab.Num(2))
    assert symbol_rep(lab.Num(1) / 2) == symbol_rep(1 / lab.Num(2))
    assert symbol_rep(lab.Num(1) - 2) == symbol_rep(1 - lab.Num(2))


def _compare_displays(expression, expected):
    assert symbol_rep(safe_eval(repr(expression))) == symbol_rep(safe_eval(expected[0]))
    assert str(expression) == expected[1]


def test_display_1():
    exp = lab.Add(lab.Num(0), lab.Var('x'))
    expected = ("Add(Num(0), Var('x'))", '0 + x')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Var('x'), lab.Num(0))
    expected = ("Add(Var('x'), Num(0))", 'x + 0')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Num(1), lab.Var('x'))
    expected = ("Mul(Num(1), Var('x'))", '1 * x')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Var('x'), lab.Num(1))
    expected = ("Mul(Var('x'), Num(1))", 'x * 1')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Var('x'), lab.Num(0))
    expected = ("Sub(Var('x'), Num(0))", 'x - 0')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Var('x'), lab.Num(1))
    expected = ("Div(Var('x'), Num(1))", 'x / 1')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Num(0), lab.Var('x'))
    expected = ("Div(Num(0), Var('x'))", '0 / x')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Num(20), lab.Num(30))
    expected = ('Add(Num(20), Num(30))', '20 + 30')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Num(50), lab.Num(80))
    expected = ('Sub(Num(50), Num(80))', '50 - 80')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Num(40), lab.Num(20))
    expected = ('Div(Num(40), Num(20))', '40 / 20')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Num(101), lab.Num(121))
    expected = ('Mul(Num(101), Num(121))', '101 * 121')
    _compare_displays(exp, expected)


def test_display_2():
    exp = lab.Add(lab.Num(0), lab.Mul(lab.Var('y'), lab.Num(2)))
    expected = ("Add(Num(0), Mul(Var('y'), Num(2)))", '0 + y * 2')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Mul(lab.Var('z'), lab.Num(3)), lab.Num(0))
    expected = ("Add(Mul(Var('z'), Num(3)), Num(0))", 'z * 3 + 0')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Num(1), lab.Add(lab.Var('A'), lab.Var('x')))
    expected = ("Mul(Num(1), Add(Var('A'), Var('x')))", '1 * (A + x)')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Sub(lab.Var('x'), lab.Var('A')), lab.Num(1))
    expected = ("Mul(Sub(Var('x'), Var('A')), Num(1))", '(x - A) * 1')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Mul(lab.Var('x'), lab.Num(3)), lab.Num(0))
    expected = ("Sub(Mul(Var('x'), Num(3)), Num(0))", 'x * 3 - 0')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Mul(lab.Num(7), lab.Var('A')), lab.Num(1))
    expected = ("Div(Mul(Num(7), Var('A')), Num(1))", '7 * A / 1')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Num(0), lab.Add(lab.Var('A'), lab.Num(3)))
    expected = ("Div(Num(0), Add(Var('A'), Num(3)))", '0 / (A + 3)')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Add(lab.Num(0), lab.Var('x')), lab.Var('z'))
    expected = ("Mul(Add(Num(0), Var('x')), Var('z'))", '(0 + x) * z')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Add(lab.Var('x'), lab.Num(0)), lab.Var('A'))
    expected = ("Sub(Add(Var('x'), Num(0)), Var('A'))", 'x + 0 - A')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Mul(lab.Num(1), lab.Var('x')), lab.Var('y'))
    expected = ("Add(Mul(Num(1), Var('x')), Var('y'))", '1 * x + y')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Var('z'), lab.Mul(lab.Var('x'), lab.Num(1)))
    expected = ("Add(Var('z'), Mul(Var('x'), Num(1)))", 'z + x * 1')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Var('A'), lab.Sub(lab.Var('x'), lab.Num(0)))
    expected = ("Sub(Var('A'), Sub(Var('x'), Num(0)))", 'A - (x - 0)')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Var('y'), lab.Div(lab.Var('x'), lab.Num(1)))
    expected = ("Div(Var('y'), Div(Var('x'), Num(1)))", 'y / (x / 1)')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Var('z'), lab.Div(lab.Num(0), lab.Var('x')))
    expected = ("Mul(Var('z'), Div(Num(0), Var('x')))", 'z * 0 / x')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Mul(lab.Num(0), lab.Var('y')), lab.Var('x'))
    expected = ("Add(Mul(Num(0), Var('y')), Var('x'))", '0 * y + x')
    _compare_displays(exp, expected)

    exp = lab.Add(lab.Var('x'), lab.Sub(lab.Num(2), lab.Num(2)))
    expected = ("Add(Var('x'), Sub(Num(2), Num(2)))", 'x + 2 - 2')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var('x'))
    expected = ("Mul(Div(Num(2), Num(2)), Var('x'))", '2 / 2 * x')
    _compare_displays(exp, expected)

    exp = lab.Mul(lab.Var('x'), lab.Sub(lab.Num(3), lab.Num(2)))
    expected = ("Mul(Var('x'), Sub(Num(3), Num(2)))", 'x * (3 - 2)')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Var('x'), lab.Mul(lab.Num(0), lab.Var('z')))
    expected = ("Sub(Var('x'), Mul(Num(0), Var('z')))", 'x - 0 * z')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Var('x'), lab.Num(1))
    expected = ("Div(Var('x'), Num(1))", 'x / 1')
    _compare_displays(exp, expected)

    exp = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var('x'))
    expected = ("Div(Add(Num(0), Num(0)), Var('x'))", '(0 + 0) / x')
    _compare_displays(exp, expected)

    exp = read_expected('41_in.pyobj')
    expected = read_expected('41_out.pyobj')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
    expected = ('Sub(Add(Num(70), Num(50)), Num(80))', '70 + 50 - 80')
    _compare_displays(exp, expected)

    exp = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
    expected = ('Sub(Num(80), Div(Num(40), Num(20)))', '80 - 40 / 20')
    _compare_displays(exp, expected)

    exp = read_expected('44_in.pyobj')
    expected = read_expected('44_out.pyobj')
    _compare_displays(exp, expected)


def test_display_3():
    exp = read_expected('45_in.pyobj')
    expected = read_expected('45_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('46_in.pyobj')
    expected = read_expected('46_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('47_in.pyobj')
    expected = read_expected('47_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('48_in.pyobj')
    expected = read_expected('48_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('49_in.pyobj')
    expected = read_expected('49_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('50_in.pyobj')
    expected = read_expected('50_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('51_in.pyobj')
    expected = read_expected('51_out.pyobj')
    _compare_displays(exp, expected)

    exp = read_expected('52_in.pyobj')
    expected = read_expected('52_out.pyobj')
    _compare_displays(exp, expected)



def test_derivative():
    exp = lab.Add(lab.Var('x'), lab.Mul(lab.Var('x'), lab.Var('x')))
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('53_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = read_expected('54_in.pyobj')
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('54_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = read_expected('55_in.pyobj')
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('55_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = lab.Mul(lab.Mul(lab.Var('x'), lab.Var('x')), lab.Var('x'))
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('56_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = lab.Mul(lab.Mul(lab.Var('x'), lab.Var('y')), lab.Var('z'))
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('57_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = read_expected('58_in.pyobj')
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('58_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = lab.Add(lab.Add(lab.Num(0), lab.Var('y')), lab.Var('x'))
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = read_expected('59_out.pyobj')
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)

    exp = lab.Num(0)
    out = (exp.deriv('x'), exp.deriv('y'), exp.deriv('x').deriv('x').deriv('x'), exp.deriv('y').deriv('x'), exp.deriv('z'))
    expected = [lab.Num(0), lab.Num(0), lab.Num(0), lab.Num(0), lab.Num(0)]
    for res, exp in zip(out, expected):
        assert symbol_rep(res) == symbol_rep(exp)



def test_simplify_1():
    expr = lab.Add(lab.Num(0), lab.Var('x'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Var('x'), lab.Num(0))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Num(1), lab.Var('x'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Var('x'), lab.Num(1))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Var('x'), lab.Num(0))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Var('x'), lab.Num(1))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Num(0), lab.Var('x'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(0)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Num(20), lab.Num(30))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(50)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Num(50), lab.Num(80))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(-30)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Num(40), lab.Num(20))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(2.0)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Num(101), lab.Num(121))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(12221)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

def test_simplify_2():
    expr = lab.Add(lab.Num(0), lab.Mul(lab.Var('y'), lab.Num(2)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Mul(lab.Var('y'), lab.Num(2))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Mul(lab.Var('z'), lab.Num(3)), lab.Num(0))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Mul(lab.Var('z'), lab.Num(3))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Num(1), lab.Add(lab.Var('A'), lab.Var('x')))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Add(lab.Var('A'), lab.Var('x'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Sub(lab.Var('x'), lab.Var('A')), lab.Num(1))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Sub(lab.Var('x'), lab.Var('A'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Mul(lab.Var('x'), lab.Num(3)), lab.Num(0))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Mul(lab.Var('x'), lab.Num(3))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Mul(lab.Num(7), lab.Var('A')), lab.Num(1))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Mul(lab.Num(7), lab.Var('A'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Num(0), lab.Add(lab.Var('A'), lab.Num(3)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(0)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Add(lab.Num(0), lab.Var('x')), lab.Var('z'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Mul(lab.Var('x'), lab.Var('z'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Add(lab.Var('x'), lab.Num(0)), lab.Var('A'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Sub(lab.Var('x'), lab.Var('A'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Mul(lab.Num(1), lab.Var('x')), lab.Var('y'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Add(lab.Var('x'), lab.Var('y'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Var('z'), lab.Mul(lab.Var('x'), lab.Num(1)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Add(lab.Var('z'), lab.Var('x'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Var('A'), lab.Sub(lab.Var('x'), lab.Num(0)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Sub(lab.Var('A'), lab.Var('x'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Var('y'), lab.Div(lab.Var('x'), lab.Num(1)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Div(lab.Var('y'), lab.Var('x'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Var('z'), lab.Div(lab.Num(0), lab.Var('x')))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(0)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Mul(lab.Num(0), lab.Var('y')), lab.Var('x'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Var('x'), lab.Sub(lab.Num(2), lab.Num(2)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Div(lab.Num(2), lab.Num(2)), lab.Var('x'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Mul(lab.Var('x'), lab.Sub(lab.Num(3), lab.Num(2)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Var('x'), lab.Mul(lab.Num(0), lab.Var('z')))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Var('x'), lab.Num(1))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Add(lab.Num(0), lab.Num(0)), lab.Var('x'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(0)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('93_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(800)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Add(lab.Num(70), lab.Num(50)), lab.Num(80))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(40)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Sub(lab.Num(80), lab.Div(lab.Num(40), lab.Num(20)))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Num(78.0)
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('96_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Add(lab.Num(20), lab.Mul(lab.Num(101), lab.Var('z')))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

def test_simplify_3():
    expr = read_expected('97_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('97_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('98_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('98_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('99_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('99_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Add(lab.Num(-1), lab.Var('h'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Add(lab.Num(-1), lab.Var('h'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('101_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('101_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('102_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('102_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('103_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('103_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('104_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('104_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = lab.Div(lab.Var('M'), lab.Var('D'))
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = lab.Div(lab.Var('M'), lab.Var('D'))
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep

    expr = read_expected('106_in.pyobj')
    orep = symbol_rep(expr)
    result = expr.simplify()
    expected = read_expected('106_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)
    assert symbol_rep(expr) == orep



def test_eval_1():
    result = lab.Add(lab.Num(0), lab.Var('x'))
    result = result.eval({'x': -15})
    expected = -15
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Mul(lab.Num(1), lab.Var('x'))
    result = result.eval({'x': -4})
    expected = -4
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Mul(lab.Var('y'), lab.Num(2))
    result = result.eval({'y': -109})
    expected = -218
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Add(lab.Mul(lab.Var('z'), lab.Num(3)), lab.Num(0))
    result = result.eval({'z': 696})
    expected = 2088
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Div(lab.Mul(lab.Num(7), lab.Var('A')), lab.Num(9))
    result = result.eval({'A': -820})
    expected = -637.7777777777778
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Add(lab.Var('z'), lab.Add(lab.Var('x'), lab.Num(1)))
    result = result.eval({'z': 253, 'x': 837})
    expected = 1091
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Sub(lab.Var('A'), lab.Add(lab.Var('x'), lab.Var('A')))
    result = result.eval({'A': -195, 'x': 279})
    expected = -279
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Div(lab.Var('y'), lab.Div(lab.Var('x'), lab.Var('z')))
    result = result.eval({'z': -101, 'x': 665, 'y': -923})
    expected = 140.18496240601505
    assert abs(result/expected - 1) <= 1e-4

    result = lab.Mul(lab.Mul(lab.Var('x'), lab.Var('y')), lab.Var('z'))
    result = result.eval({'z': -875, 'x': -263, 'y': -142})
    expected = -32677750
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('116_in.pyobj')
    result = result.eval({'A': -413, 'z': -632, 'x': 253, 'y': 779})
    expected = -23520
    assert abs(result/expected - 1) <= 1e-4


def test_eval_2():
    result = read_expected('117_in.pyobj')
    result = result.eval({'y': 745, 'Q': -439, 't': 590, 'h': -543, 'x': -152, 'j': 582, 'L': 761, 'P': -742, 'b': -979, 'z': -606, 'd': -736, 'D': -33, 'v': 346, 'J': 235, 'T': 695, 'I': 36, 'N': -323, 'M': -618, 'r': 484, 'n': 93, 'K': -800, 'i': -790, 'w': -9, 'G': -528, 'Y': -109, 'e': 196, 'O': -68, 'H': -195, 'A': -268, 'c': 372, 'u': 448, 'U': 464, 'k': 715, 'E': 267, 'Z': 703, 'a': -525, 'B': 413, 'F': -319, 'l': -966, 'm': -278})
    expected = -1.6527112541986483e-06
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('118_in.pyobj')
    result = result.eval({'y': 674, 'Q': -53, 'W': 263, 't': -232, 'h': 64, 'x': -797, 'o': 269, 'L': -984, 'P': -521, 'd': 219, 'v': -462, 'T': -705, 'J': 793, 'D': -395, 'I': -488, 'N': -563, 'M': 400, 'r': 100, 'p': 220, 'n': 100, 'g': -611, 'K': 13, 'V': -286, 'i': -161, 'G': 446, 'Y': 723, 'e': 845, 'O': -351, 'S': 971, 'H': -456, 'A': -104, 'c': -405, 'u': 108, 'U': 530, 'k': 79, 's': -363, 'Z': 827, 'f': -162, 'E': -253, 'q': 266, 'a': 957, 'B': -294, 'F': 884, 'R': -614, 'l': 690, 'X': 142, 'm': 626, 'C': -725})
    expected = 220799027764.14496
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('119_in.pyobj')
    result = result.eval({'y': 520, 'Q': -285, 'W': 496, 'x': -554, 'j': 572, 'o': -128, 'L': 296, 'P': 894, 'b': -151, 'z': 862, 'd': -160, 'D': -37, 'J': -128, 'v': 232, 'T': -334, 'I': 877, 'M': 715, 'N': 234, 'r': -327, 'n': 999, 'g': -311, 'p': 238, 'K': 448, 'V': 71, 'i': -247, 'w': -562, 'G': 773, 'Y': 25, 'e': -226, 'O': 369, 'S': -534, 'H': 214, 'A': 492, 'c': 495, 'u': -912, 's': -355, 'k': 650, 'Z': -527, 'f': -255, 'q': -629, 'B': -38, 'F': 800, 'R': -298, 'X': 245, 'm': -690, 'C': 862})
    expected = 112954135735.31244
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('120_in.pyobj')
    result = result.eval({'y': -964, 'Q': 211, 'W': 361, 't': -149, 'j': 502, 'o': 82, 'h': 69, 'x': -552, 'L': 266, 'P': 294, 'z': -536, 'J': 310, 'T': -434, 'N': -671, 'r': -538, 'p': -521, 'n': -53, 'g': -548, 'K': -586, 'i': 403, 'w': 464, 'G': 819, 'V': -886, 'Y': -371, 'e': 977, 'O': 472, 'H': -555, 'c': 203, 'u': 615, 'U': -176, 's': -285, 'Z': 350, 'f': -94, 'q': -825, 'a': -646, 'B': -246, 'F': -685, 'R': -949, 'l': 258, 'X': 450, 'm': 353})
    expected = 673268849601579.5
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('121_in.pyobj')
    result = result.eval({'e': -415, 'h': 497, 'c': 439, 't': -558, 'j': -786, 'X': -421, 'U': 427, 's': 589, 'Z': -688, 'f': -341, 'L': -29, 'b': -73, 'v': -477, 'T': 975, 'a': 422, 'I': -209, 'F': -665, 'l': 901, 'r': 42, 'n': 497, 'K': 653, 'V': -353, 'w': 788, 'G': 443, 'm': -109, 'Y': 341})
    expected = -262.66666666753156
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('122_in.pyobj')
    result = result.eval({'O': 307, 'Q': 955, 'S': -389, 'c': -730, 'x': 889, 't': -235, 'U': 915, 'k': 197, 's': 819, 'Z': -353, 'E': -621, 'L': -850, 'q': -65, 'V': 549, 'T': -740, 'J': -455, 'F': 433, 'N': 55, 'R': 122, 'p': 950, 'K': -1000, 'i': -430, 'w': -592, 'Y': 782, 'C': -279})
    expected = 295.03505160344514
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('123_in.pyobj')
    result = result.eval({'e': -259, 'y': 801, 'S': 460, 'W': -769, 't': -225, 'x': 453, 'o': 128, 'u': -207, 'h': 229, 'j': 789, 'U': 637, 's': 40, 'k': -604, 'Z': -280, 'f': 187, 'L': 835, 'E': 473, 'P': -208, 'b': 520, 'D': 557, 'v': -111, 'F': -205, 'M': 221, 'R': -141, 'r': 847, 'g': -873, 'X': 140, 'm': -407, 'C': -573})
    expected = 4.08734422758323
    assert abs(result/expected - 1) <= 1e-4

    result = read_expected('124_in.pyobj')
    result = result.eval({'e': -771, 'O': -165, 'S': -356, 'Q': 889, 'H': 529, 'W': -71, 'o': -505, 'u': -889, 'U': 323, 'k': -975, 's': 157, 'E': 168, 'Z': 796, 'f': -109, 'b': 1, 'd': -973, 'v': 243, 'D': -511, 'T': -846, 'B': -181, 'J': -372, 'R': 873, 'N': 712, 'l': -411, 'r': 286, 'g': -257, 'K': 699, 'i': 892, 'X': 350, 'G': 222, 'm': -313, 'C': -960})
    expected = 454.45125382620444
    assert abs(result/expected - 1) <= 1e-4



def test_parse_1():
    result = lab.sym('x')
    expected = lab.Var('x')
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('20')
    expected = lab.Num(20)
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(0 + x)')
    expected = lab.Add(lab.Num(0), lab.Var('x'))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(-101 * x)')
    expected = lab.Mul(lab.Num(-101), lab.Var('x'))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(y * -2)')
    expected = lab.Mul(lab.Var('y'), lab.Num(-2))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('((z * 3) + 0)')
    expected = lab.Add(lab.Mul(lab.Var('z'), lab.Num(3)), lab.Num(0))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('((7 * A) / 9)')
    expected = lab.Div(lab.Mul(lab.Num(7), lab.Var('A')), lab.Num(9))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(z + (x + 1))')
    expected = lab.Add(lab.Var('z'), lab.Add(lab.Var('x'), lab.Num(1)))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(A - (x + A))')
    expected = lab.Sub(lab.Var('A'), lab.Add(lab.Var('x'), lab.Var('A')))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(y / (x / z))')
    expected = lab.Div(lab.Var('y'), lab.Div(lab.Var('x'), lab.Var('z')))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('((x * y) * z)')
    expected = lab.Mul(lab.Mul(lab.Var('x'), lab.Var('y')), lab.Var('z'))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('((x + A) * (y + z))')
    expected = read_expected('136_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)


def test_parse_2():
    result = lab.sym(read_expected('137_in.pyobj'))
    expected = read_expected('137_out.pyobj') 
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(o * N)')
    expected = lab.Mul(lab.Var('o'), lab.Var('N'))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym(read_expected('139_in.pyobj'))
    expected = read_expected('139_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym(read_expected('140_in.pyobj'))
    expected = read_expected('140_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym(read_expected('141_in.pyobj'))
    expected = read_expected('141_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym(read_expected('142_in.pyobj'))
    expected = read_expected('142_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym('(b + 9)')
    expected = lab.Add(lab.Var('b'), lab.Num(9))
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym(read_expected('144_in.pyobj'))
    expected = read_expected('144_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)

    result = lab.sym(read_expected('145_in.pyobj'))
    expected = read_expected('145_out.pyobj')
    assert symbol_rep(result) == symbol_rep(expected)



if __name__ == '__main__':
    import sys
    import json

    class TestData:
        def __init__(self):
            self.results = {'passed': []}

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != 'call':
                return
            self.results.setdefault(report.outcome, []).append(report.head_line)

        def pytest_collection_finish(self, session):
            self.results['total'] = [i.name for i in session.items]

        def pytest_unconfigure(self, config):
            print(json.dumps(self.results))

    if os.environ.get('CATSOOP'):
        args = ['--color=yes', '-v', __file__]
        if len(sys.argv) > 1:
            args = ['-k', sys.argv[1], *args]
        kwargs = {'plugins': [TestData()]}
    else:
        args = ['-v', __file__] if len(sys.argv) == 1 else ['-v', *('%s::%s' % (__file__, i) for i in sys.argv[1:])]
        kwargs = {}
    res = pytest.main(args, **kwargs)
