import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    def __add__(self, other):
        """
        overrides behavior of + where E1 + E2 results in an instance Add(E1, E2)
        given that E1 is a Symbol instance
        """
        return Add(self, other)
    
    def __radd__(self, other):
        """
        overrides behavior of + where E1 + E2 results in an instance Add(E1, E2)
        given that E1 is not a Symbol instance, but E2 is
        """
        return Add(other, self)

    def __sub__(self, other):
        """
        overrides behavior of - where E1 - E2 results in an instance Sub(E1, E2)
        given that E1 is a Symbol instance
        """
        return Sub(self, other)
    
    def __rsub__(self, other):
        """
        overrides behavior of - where E1 - E2 results in an instance Sub(E1, E2)
        given that E1 is not a Symbol instance, but E2 is
        """
        return Sub(other, self)
    
    def __mul__(self, other):
        """
        overrides behavior of * where E1 * E2 results in an instance Mul(E1, E2)
        given that E1 is a Symbol instance
        """
        return Mul(self, other)
    
    def __rmul__(self, other):
        """
        overrides behavior of * where E1 * E2 results in an instance Mul(E1, E2)
        given that E1 is not a Symbol instance, but E2 is
        """
        return Mul(other, self) 
    
    def __truediv__(self, other):
        """
        overrides behavior of / where E1 / E2 results in an instance Div(E1, E2)
        given that E1 is a Symbol instance
        """
        return Div(self, other)
    
    def __rtruediv__(self, other):
        """
        overrides behavior of / where E1 / E2 results in an instance Sub(E1, E2)
        given that E1 is not a Symbol instance, but E2 is
        """
        return Div(other, self)
    
        
class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        
    class_name = 'Var' # class variable

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'
    
    def deriv(self, x):
        """
        Return 1 if derivative taken with respect to same variable. 0 otherwise
        """
        if self.name == x: return Num(1)
        return Num(0)
    
    def simplify(self):
        return self
    
    def eval_helper(self, dic):
        """
        Return Num instance if value corresponding to variable is present in dictionary.
        Otherwise return Variable instance
        """
        if self.name in dic:
            return Num(dic[self.name])
        return self
    
    def eval(self, dic):
        """
        Return value associated with variable if in dictionary. Otherwise return variable name
        """
        if self.name in dic:
            return dic[self.name]
        return self.name


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    class_name = 'Num' # class variable
    
    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'
    
    def deriv(self, x):
        """
        Return 0 since we are taking the derivative of a constant
        """
        return Num(0)
    
    def simplify(self):
        return self
    
    def eval_helper(self, dic):
        """
        Return Num Instance
        """
        return self
    
    def eval(self, dic):
        """
        Return value associated with the Num instance
        """
        return self.n
    
class BinOp(Symbol):
    def __init__(self, left, right):
        """
        Initializer.  Store an instance variables left and right, containing the
        values passed in to the initializer, which must be of type Symbol, int, float or string.
        """
        L = [left, right]
        for i in range(len(L)):
            if isinstance(L[i], Symbol):
                continue
            elif isinstance(L[i], int) or isinstance(L[i], float):
                L[i] = Num(L[i])
            elif isinstance(L[i], str):
                L[i] = Var(L[i])
            else:
                raise TypeError("Incorrect Argument Type: must be of type Symbol, int, float, or string")
        self.left = L[0]
        self.right = L[1]
        
    def __repr__(self):
        """
        Get string representation of Binop instance that can be evaluated
        """
        return self.class_name + '(' + repr(self.left) + ',' + repr(self.right) + ')'
    
    def __str__(self):
        """
        Get readable string representation of BinOp instance
        """
        left = str(self.left)
        right = str(self.right)
        op = ' ' + self.op + ' '

        # place brackets according to PEDMAS
        if self.class_name == 'Mul' or self.class_name == 'Div':
            if self.left.class_name == 'Add' or self.left.class_name == 'Sub':
                left = '(' + left + ')'
            if self.right.class_name == 'Add' or self.right.class_name == 'Sub':
                right =  '(' + right + ')'
        if (self.class_name == 'Sub' and (self.right.class_name == 'Sub' or self.right.class_name == 'Add')) or \
        (self.class_name == 'Div' and (self.right.class_name == 'Div' or self.right.class_name == 'Mul')):
            right = '(' + right + ')'
            
        return left + op + right
    
    def eval(self, dic):
        """
        Substitute variables for values in dictionary and evaluate instance. Return string representation
        if values for all variables not given
        
        >>> q = Mul(Num(3), Add(Var('A'), Var('x')))
        >>> q.eval({'x':2, 'A': 4})
        18
        >>> q.eval({'x': 2})
        '3 * (A + 2)'
        """
        x = self.eval_helper(dic)
        if x.class_name == 'Num': return x.n # return int or float if result of eval_helper is a Num instance
        return str(x)
    
     

class Add(BinOp):

    op =  '+'
    class_name = 'Add'
    
    def deriv(self, x):
        """
        Get derivative of a sum
        """
        return self.left.deriv(x) + self.right.deriv(x)
    
    def simplify(self):
        """
        Return simplified expression
        """
        
        x = Add(self.left.simplify(), self.right.simplify()) # call simplify on left and right variables
        
        if type(x.left) == Num and type(x.right) == Num:
            return Num(x.left.n + x.right.n) # add values if both left and right are numbers
        # check if left or right is zero, return the other
        if isinstance(x.left, Num) and x.left.n == 0:
            return x.right.simplify()
        if isinstance(x.right, Num) and x.right.n == 0:
            return x.left.simplify()

        return x
    
    def eval_helper(self, dic):
        """
        Return simplified Add instance after substituting values in dictionary
        """
        l = self.left.eval_helper(dic)
        r = self.right.eval_helper(dic)
        return Add(l, r).simplify()

    
class Sub(BinOp):

    op = '-'
    class_name = 'Sub'
    
    def deriv(self, x):
        """
        Get derivative of a sub
        """
        return self.left.deriv(x) - self.right.deriv(x)
    
    def simplify(self):
        """
        Return simplified expression
        """
        
        x = Sub(self.left.simplify(), self.right.simplify())

        if type(x.left) == Num and type(x.right) == Num:
            return Num(x.left.n - x.right.n)
        
        if isinstance(x.right, Num) and x.right.n == 0: # subtracting 0 from left
            return x.left.simplify() 
        
        return x
    
    def eval_helper(self, dic):
        """
        Return simplified Sub instance after substituting values in dictionary
        """
        l = self.left.eval_helper(dic)
        r = self.right.eval_helper(dic)
        return Sub(l, r).simplify()



class Mul(BinOp):

    op = '*'
    class_name = 'Mul'
    
    def deriv(self, x):
        """
        Derivative of a product
        """
        return self.left * self.right.deriv(x) + (self.right * self.left.deriv(x))
    
    def simplify(self):
        """
        Return simplified expression
        """
        
        x = Mul(self.left.simplify(), self.right.simplify())
        
        # check if left or right is zero
        if (isinstance(x.left, Num) and x.left.n == 0) or (isinstance(x.right, Num) and x.right.n == 0):
            return Num(0)
        
        # check if left or right is 1
        if isinstance(x.left, Num) and x.left.n == 1:
            return x.right.simplify()
        
        if isinstance(x.right, Num) and x.right.n == 1:
            return x.left.simplify()
        
        # check if left and right are both numbers
        if type(x.left) == Num and type(x.right) == Num:
            return Num(x.left.n * x.right.n)
        
        return x
    
    def eval_helper(self, dic):
        """
        Return simplified Mul instance after substituting values in dictionary
        """
        l = self.left.eval_helper(dic)
        r = self.right.eval_helper(dic)
        return Mul(l, r).simplify()

        
        
class Div(BinOp):

    op = '/'
    class_name = 'Div'
    
    def deriv(self, x):
        """
        Derivative of a quotient
        """
        return (self.right * self.left.deriv(x) - self.left * self.right.deriv(x)) / self.right * self.right
    
   
    def simplify(self):
        """
        Return simplified expression
        """
        
        x =  Div(self.left.simplify(), self.right.simplify())

        # check if left is 0
        if isinstance(x.left, Num) and x.left.n == 0:
            return Num(0)
        
        # check if right is 1
        if isinstance(x.right, Num) and x.right.n == 1:
            return self.left.simplify()
        
        # check if both left and right are numbers
        if type(x.left) == Num and type(x.right) == Num:
            return Num(x.left.n / x.right.n)
        
        return x
    
    def eval_helper(self, dic):
        """
        Return simplified Div instance after substituting values in dictionary
        """
        l = self.left.eval_helper(dic)
        r = self.right.eval_helper(dic)
        return Div(l, r).simplify()


def is_number(x):
    """
    Return True if x is an int or float. Otherwise return False
    """
    try:
        float(x)
        return True
    except ValueError:
        return False
    
def find_op(x, num):
    """
    Search through string x starting from index num for an operator. Return operator
    and position of operator in string
    """
    for idx, char in enumerate(x[num:]):
        if char in ["+", "-", "*", "/"]:
            return (idx + num, char)
        
def isfloat(x):
    """
    Return True if x is a float
    """
    for char in x:
        if char == ".":
            return True
    return False


def closing_idx(x):
    """
    Find index of string x where ')' occurs to close the second open bracket of string
    """
    count = 1
    for idx, char in enumerate(x[2:]): # start from two to avoid first two open brackets
        if char == ")":
            count -= 1
        if char == "(":
            count += 1
        if count == 0:
            return idx + 2

def sym(exp):
    """
    Parse string input, exp, and return a Symbol instance
    """
    if exp[0] != '(': # single expression of type variable or number
        if is_number(exp):
            if isfloat(exp):
                return Num(float(exp))
            else:
                return Num(int(exp))
        else:
            return Var(exp)
    
    if exp[1] == "(":
        idx, op = find_op(exp, closing_idx(exp))
    else:
        idx, op = find_op(exp, 2) # start at position two to avoid a left negative number
    # receursively apply sym on left and right strings
    left = sym(exp[1:idx - 1]) # start from 1 to avoid first open bracket
    right = sym(exp[idx + 2: -1]) # stop at -1 to avoid last closing bracket
    # return correct BinOp subclass instance based on operator
    if op == "+":
        return Add(left, right)
    elif op == "-":
        return Sub(left, right)
    elif op == "*":
        return Mul(left, right)
    else:
        return Div(left, right)
    
            


if __name__ == '__main__':
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    # x = Var('x')
    # y = Var('y')
    # z = 2*x-x*y + 3*y
    # lol = z.deriv('x')
    # print(lol)
    # print(lol.simplify())
    # lal = z.deriv('y')
    # print(lal)
    # # print(repr(lal))
    # k = lal.simplify()
    # print(repr(k))
    # print(k)
    # print(Add(Add(Num(2), Num(-2)), Add(Var('x'), Num(0))).simplify())
    # z = Mul(Var('x'), Sub(Var('y'), Mul(Var('z'), Num(2))))
    # print(z.eval({'z': 9}))
    # print(z.eval({'x': 3, 'y': 10, 'z': 2}))
    # print(repr(sym('(x * (2 + 3))')))
    # print(repr(sym('(x - (-1.01 + -x))')))
    q = Mul(Num(3), Add(Var('A'), Var('x')))
    print(q.eval({'x': 2, 'A': 5}))
    exp = Add(Num(0), Var('x'))
    print(exp.eval({'x': -15}))
    