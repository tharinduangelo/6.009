#!/usr/bin/env python3
"""6.009 Lab 9: Snek Interpreter"""

import doctest
# NO ADDITIONAL IMPORTS!


###########################
# Snek-related Exceptions #
###########################

class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    
    def __init__(self, *message):
        
        self.message = "SnekSyntaxError"
        if message != ():
            self.message += ": " + message[0]
    
    def __str__(self):
        return self.message


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    
    def __init__(self, *message):
        
        self.message = "SnekNameError"
        if message != ():
            self.message += ": " + message[0]
    
    def __str__(self):
        return self.message


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """

    def __init__(self, *message):
        
        self.message = "SnekEvaluationError"
        if message != ():
            self.message += ": " + message[0]
    
    def __str__(self):
        return self.message
    
class SnekZeroDivisionError(SnekEvaluationError):
    
    def __str__(self):
        return "SnekZeroDivisionError: division by zero"


############################
# Tokenization and Parsing #
############################

def remove_comments(source):
    """
    Takes an input string and removes all comments
    
    >>> remove_comments("Hello there ; this is a comment")
    'Hello there '
    """
    start_index = 0
    while True:
        i = source.find(';', start_index)
        if i == -1: break
        j = source.find('\n', i)
        if j == -1: #no new line character
            source = source[:i]
            break
        source = source[:i] + source[j + 1:]
        start_index = i
    return source

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
                      
    >>> tokenize("(foo (bar 3.14))")
    ['(', 'foo', '(', 'bar', '3.14', ')', ')']
    """
    return remove_comments(source).replace('(', ' ( ').replace(')', ' ) ').split()

def closing_idx(x, index):
    """
    Find index of list x where ')' occurs to close the open bracket of string occuring at index given
    
    >>> closing_idx("(h(e)llo) there", 0)
    8
    """
    count = 1
    for idx, char in enumerate(x[index + 1:]):
        if char == "(":
            count += 1
        if char == ")":
            count -= 1
        if count == 0:
            return idx + index + 1

        
def brackets_to_lists(tokens):
    """
    Converts all brackets in string into python lists
    
    >>> brackets_to_lists(['(','cat','(','dog','(','tomato',')',')',')'])
    [['cat', ['dog', ['tomato']]]]
    """
    try:
        i = tokens.index('(')
    except ValueError:
        return tokens
    j = closing_idx(tokens, i)
    tokens = tokens[:i] + [brackets_to_lists(tokens[i + 1: j])] + brackets_to_lists(tokens[j+ 1: ])
    return tokens

def is_number(x):
    """
    Return True if x is an int or float. Otherwise return False
    
    >>> is_number('2')
    True
    """
    try:
        float(x)
        return True
    except ValueError:
        return False

def isfloat(x):
    """
    Return True if x is a float
    
    >>> isfloat('2.3')
    True
    """
    for char in x:
        if char == ".":
            return True
    return False

def check_paren(tokens, k = 0):
    """
    Raise SnekSyntax Error if there is a mismatch in parentheses in tokens.
    Second argument is used to denote where to search next ')' from.
    Returns None
    
    >>> check_paren("(he)l)lo(")
    Traceback (most recent call last):
     ...
    SnekSyntaxError: SnekSyntaxError: '(' and ')' occur in wrong order
    """
    try:
        i = tokens.index('(')
    except ValueError: # no '('
        try:
            j = tokens[k: ].index(')')
        except ValueError: # no '(' or ')'
            return # no issues
        raise SnekSyntaxError("too many right parentheses in input")
    try:
        j = tokens[k: ].index(')') + k
    except ValueError:
        raise SnekSyntaxError("too many left parentheses in input")
    if i > j:
        raise SnekSyntaxError("'(' and ')' occur in wrong order")
    k = j + 1 # set index to search for ')' from to j + 1
    check_paren(tokens[i + 1: ], k - i - 1)

def check_first_bracket(tokens):
    """
    raise SnekSyntaxError if input is not an atomic expression but doesn't have brackets
    
    >>> check_first_bracket("['x', 3]")
    Traceback (most recent call last):
     ...
    SnekSyntaxError: SnekSyntaxError: input is not an atomic expression, missing parentheses    
    """
    
    try:
        tokens.index('(')
    except ValueError:
        if len(tokens) > 1: raise SnekSyntaxError("input is not an atomic expression, missing parentheses")

def check_assignment(res):
    """
    if res is an assignment statement, check if it is syntactically valid
    if assignment statement is a function definition in shorthand notation, convert to normal notation
    and return
    
    >>> check_assignment([':=', 7, 8])
    Traceback (most recent call last):
     ...
    SnekSyntaxError: SnekSyntaxError: cannot assign to a literal    
    """
    if res == ':=':
        raise SnekSyntaxError("invalid syntax")
    if isinstance(res, list) and res[0] == ':=':
        if len(res) != 3:
            raise SnekSyntaxError(f"incorrect number of arguments for assignment, 3 needed, {len(res)} given")
        if isinstance(res[1], (int, float)):
            raise SnekSyntaxError("cannot assign to a literal")
        if isinstance(res[1], list): # treat list as a function definition with arbitrary parameters
            if res[1] == []: raise SnekSyntaxError("cannot assign to a literal")
            if isinstance(res[1][0], (int, float)): raise SnekSyntaxError("cannot assign to a literal")
            if any(isinstance(i, (int, float)) for i in res[1][1:]): raise SnekSyntaxError("arguments cannot be numbers")
            if len(res[1]) == 1:
                res = [res[0], res[1][0], ['function', [], res[2]]] # no parameters for function
            else:
                res = [res[0], res[1][0], ['function', res[1][1:], res[2]]]
    return res
                         

def check_function(res):
    """ 
    Check if function expression has the correct form
    should be of length three, arguments should be a list that cannot contain numbers
    
    >>> check_function(['function', ['x','y'], ['*', 'x', 'y']])
    """
    if res == 'function': raise SnekSyntaxError('invalid syntax')
    if res == [] or isinstance(res, (int, float, str)): return # not a function expression, stop condition
    # res is a list
    if res[0] == 'function':
        if len(res) != 3 or not isinstance(res[1], list) or any(is_number(i) for i in res[1]):
            raise SnekSyntaxError('invalid syntax')
    else:
        check_function(res[0])
    check_function(res[1:]) # check rest of expression

def parse_numbers(tokens):
    """
    Parse numbers (ints and floats) in list of tokens
    
    >>> y = ['3', '2.3', 'x']
    >>> parse_numbers(y)
    >>> y
    [3, 2.3, 'x']
    """
    for idx, tok in enumerate(tokens):
        if is_number(tok):
            if isfloat(tok):
                tokens[idx] = float(tok)
            else:
                tokens[idx] = int(tok)
                
def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
        
    >>> parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
    ['+', 2, ['-', 5, 3], 7, 8]
    """
    check_first_bracket(tokens) # check is not atomic, but no brackets
    check_paren(tokens) # check for correct parentheses
    parse_numbers(tokens)# convert string representation of numbers to ints and floats
    try:
        x = brackets_to_lists(tokens)[0] # take 0th element to remove first list brackets
    except IndexError: # if nothing is passed into original input = empty list
        return tokens
    if x == []: raise SnekSyntaxError("invalid S-expression, must contain 1 or more expressions") # () as input
    x = check_assignment(x) # check for correct assginment statements
    check_function(x) # check for correct function statements
    return x

######################
# Built-in Functions #
######################

def mul(args):
    """
    Returns 1 if no arguments given. If 1 argument, return argument, else return product of arguments
    
    >>> mul([2, 5, 6])
    60
    """
    if len(args) == 0: return 1
    return args[0] * mul(args[1:])
    
def div(args):
    """
    Raise SnekEvaluationError if no arguments given. If one argument, return 1 / argument.
    Else, return first argument divided by rest of arguments. Raise ZeroDivisionError if dividing by zero
    
    >>> div([2])
    0.5
    """
    if args == []: raise SnekEvaluationError("no arguments given")
    if len(args) == 1: 
        if args[0] == 0: raise SnekZeroDivisionError
        return 1 / args[0]
    res = args[0]
    for arg in args[1:]:
        if arg == 0: raise SnekZeroDivisionError
        res /= arg
    return res

snek_builtins = {
        '+': sum,
        '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
        '*': mul,
        '/': div,     
    }



##############
# Evaluation #
##############

def replace(body,ele,val):
    """
    Replace element ele in the body of the function by val
    
    >>> x = replace(['*', 'x', 'y', 3, ['+', 'x', 1]], 'x', 4)
    >>> x
    ['*', 4, 'y', 3, ['+', 4, 1]]
    """
    if isinstance(body, (float, int, user_func)):
        return body
    if isinstance(body, str):
        if body == ele: return val
        return body
    body_copy = body[:] # make a copy of the body to prevent mutation
    for idx, tok in enumerate(body_copy):
        if tok == ele:
            body_copy[idx] = val
        if isinstance(tok, list):
            body_copy[idx] = replace(tok, ele, val)
    return body_copy


class Environment():
    
    def __init__(self, parent = None):
        """
        Initializes a new environment. Dictionary stores mappings of variables to values in
        current environment. parent is the parent environment, that the current environment belongs to.
        If there is no parent environment, parent is initialized to None
        """
        self.dic = {}
        self.parent = parent
    
    def store_var(self, x, val):
        """
        Setter, takes the variable x and stores it in self.dic with value val 
        """
        self.dic[x] = val
        

    def find_var(self, x):
        """
        Checks if variable x is present in current environment or all parent environments and
        returns value associated with it. Raises a SnekNameError if variable not found
        """  
        if x in self.dic:
            return self.dic[x]
        if self.parent == None:
            raise SnekNameError(f'name {x} is not defined')
        return self.parent.find_var(x)
    
class user_func():
    
    def __init__(self, args, body, env):
        """
        Initializes a new function object. Takes in arguments, body of function, and environment
        function was defined in. args is a list, body can be anything
        """
        self.args = args
        self.body = body
        self.env = env
        
    def __repr__(self):
        return 'function object'
    
    def __call__(self, args):
        """
        Evaluates body of the functions with list of arguments and returns result
        
        """
        if len(args) != len(self.args): raise SnekEvaluationError("incorrect number of arguments")
        if args == []: # no arguments
            return evaluate(self.body, self.env)
        body = self.body
        # replace variables in body with arguments
        for idx in range(len(args)):
            body = replace(body, self.args[idx], args[idx])
        return evaluate(body, self.env)

def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
                            
    >>> evaluate(['-', 3.14, 1.14, 1])
    1.0000000000000004
    
    >>> evaluate(['+', 3, 2, 4, ['-', 2, 7, 8]])
    -4
    
    >>> evaluate([':=', 'x', ['+', 2, 3]])
    5
    
    >>> evaluate([['function', ['x'], ['*', 'x', 'x']], 3])
    9
    """
    
    if env == None:
        env = Environment() # create new environment if none specified
        
    if isinstance(tree, (float, int, user_func)):
      return tree
    if isinstance(tree, str):
        if tree in snek_builtins:
            return snek_builtins[tree] # return built-in function
        else:
            return env.find_var(tree) # return value of variable stored, raise SnekNameError if not found
    
    #tree is a list
    if tree == []: return None # nothing passed in as input
    
    if isinstance(tree[0], (int, float)):
        if len(tree) == 1: return tree[0] # inputs of the form (3)
        raise SnekEvaluationError # for inputs of the form (3 5) or (3 x)
        
    if tree[0] == 'function':
        func = user_func(tree[1], tree[2], env) # create new user_func instance
        return func
    
    if tree[0] == ':=':
        assign = evaluate(tree[2], env) # evaulate right hand side of assignment
        env.store_var(tree[1], assign) # store variable and assignment in current environment
        return assign
                
    if isinstance(tree[0], str):
        flag = False # flag to capture built-in functions
        try:
            val = env.find_var(tree[0])
            if isinstance(val, user_func):
                return val([evaluate(i, env) for i in tree[1:]])
            if val in snek_builtins.values():
                flag = True
            if len(tree) == 1: return val # for inputs such as (x) where x is already stored
        except SnekNameError as e:
            if tree[0] in snek_builtins:
                flag = True
                val = snek_builtins[tree[0]]
            else:
                raise e # raise SnekNameError
        
        if flag: # tree[0] is a built-in function
            res = [evaluate(i, env) for i in tree[1:]]
            res_set = set(res)
            if any(i in res_set for i in snek_builtins.values()): 
                raise SnekEvaluationError(f"unsupported operand type(s) for {tree[0]}, built-in function")
            if any(isinstance(i, user_func) for i in res_set):
                raise SnekEvaluationError(f"unsupported operand type(s) for {tree[0]}, user defined function")
            return val(res)
        
        raise SnekEvaluationError(f'{tree[0]} is not a defined or built-in function')
    
    # tree[0] is a list
    x = evaluate(tree[0], env)
    if isinstance(x, user_func): # inline lambda functions like ((function (x) (* x x)) 3)
        return x([evaluate(i, env) for i in tree[1:]])
    if len(tree) == 1: # if x is an int or float
        return x
    raise SnekEvaluationError # for inputs like ((x) 3) where x is a variable, not a function

def result_and_env(tree, env = None):
    """
    Takes in parsed output, environment, and returns evaluated result and environment output was
    evaluated in
    """
    if env == None:
        env = Environment()
    
    x = evaluate(tree, env)
    
    return x, env

def repl(env = None):
    """
    A REPL ("Read, Evaluate, Print Loop") for Snek.
    continually prompts the user for input until they type QUIT
    """
    count = 0 # to keep track of input number
    while True:
        count += 1
        x = input(f'in [{count}]> ')
        if x == 'QUIT': break
        try:
            p = parse(tokenize(x))
        except SnekSyntaxError as e:
            print(e)
            continue
        try:
            res, env = result_and_env(p, env)
        except SnekNameError as e:
            print(e)
            continue
        except SnekZeroDivisionError as e:
            print(e)
            continue
        except SnekEvaluationError as e:
            print(e)
            continue
        if res == None: continue # no input given
        print(f'out [{count}]> {res}')


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    repl()
    
