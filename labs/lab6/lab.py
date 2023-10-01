#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def convert(formula):
    """
    Parameters
    ----------
    formula : a list of lists

    Returns
    -------
    a list of sets
    """
    return [set(k) for k in formula]

def set_empty(formula):
    """
    Parameters
    ----------
    formula : a list of sets

    Returns
    -------
    True if any of the sets in the formula are empty, False otherwise
    """
    return any(sub_set == set() for sub_set in formula)

def update(val, formula):
    """
    Parameters
    ----------
    val : tuple of element name and truth value
    formula : a list of sets

    Returns
    -------
    res : updated formula. If val is in a set, that set is removed. If val with opposite
    truth value is in set, that value is removed.
    None if empty set created during update process.
    
    >>> formula  = [{('a', True), ('b', True), ('c', True)},
    ...            {('a', False), ('f', True)},
    ...            {('d', False), ('e', True), ('a', True), ('g', True)},
    ...            {('h', False), ('c', True), ('a', False), ('f', True)}]
    >>> x = update(('a', True), formula)
    >>> x[0] == {('f', True)}
    True
    >>> x[1] == {('f', True), ('h', False), ('c', True)}
    True
    """
    res = []
    not_val = (val[0], not val[1]) #get variable with opposite truth value
    for sub_set in formula:
        if val in sub_set: continue # ignore set if val in it
        elif not_val in sub_set:
            if len(sub_set) == 1: return None # empty set will be created, so return None since no solution
            x = sub_set.copy()
            x.remove(not_val)
            res.append(x) # add set with not val removed
        else:
            res.append(sub_set)
    return res # return updated formula


def get_clause(formula):
    """
    Parameters
    ----------
    formula : a list of sets

    Returns
    -------
    set, of length 1 if present
    None otherwise

    >>> formula = [{('f', True)}, {('h', False), ('c', True), ('f', True)}]
    >>> get_clause(formula)
    ('f', True)
    >>> formula = [{('h', False), ('c', True), ('f', True)}]
    >>> get_clause(formula)
    """
    for sub_set in formula:
        if len(sub_set) == 1: return list(sub_set)[0]
    return None

def clause_path(formula):
    """
    Loops over formula, and updates it until there are no clauses of length 1

    Parameters
    ----------
    formula : a list of sets

    Returns
    -------
    a tuple, (agenda, formula)
    agenda : list, of tuple values that were found as one clauses in the formula
    formula : updated formula
    
    >>> formula  = [{('a', True), ('b', True), ('c', True)},
    ... {('a', False)},
    ... {('d', False), ('e', True), ('a', True), ('g', True)},
    ... {('h', False), ('c', True), ('a', False), ('f', True)}]
    
    >>> agenda, formula = clause_path(formula)
    >>> agenda == [('a', False)]
    True
    >>> formula[0] == {('c', True), ('b', True)}
    True
    >>> formula[1] == {('d', False), ('g', True), ('e', True)}
    True
    """
    agenda = [] # initialize list to store tuples in one clauses that are found
    clause = get_clause(formula)
    if clause == None: return ([], formula)
    while clause: # loop until no more one clauses remain
        agenda.append(clause)
        formula = update(clause, formula)
        if formula == None: return (agenda, formula) # if no solution exists
        clause = get_clause(formula)
    return (agenda, formula)


def dfs(formula):
    """
    Carries out a depth first search and returns a path containing truth values of elements that satisfies
    the formula
    
    Parameters
    ----------
    formula : a list of sets

    Returns
    -------
    list, of tuple values corresponding to a solution
    None, if no solution exists
    
    >>> formula = [{("a",True), ("b",True)}, {("a",False), ("b",False), ("c",True)},
    ...            {("b",True),("c",True)}, {("b",True),("c",False)}]
    >>> x = dfs(formula)
    >>> ('a', False) in x
    True
    >>> ('b', True) in x
    True
    """
    
    if formula == []: return {} # no variables present to satisfy formula
    if set_empty(formula): return None # if formula has empty set, no solution
    path, form = clause_path(formula)
    if form == None: return None
    if form == []: return path # path found
    val = next(iter(form[0])) # get tuple from formula
    agenda = [[path + [val], form], [path+[(val[0], not val[1])], form]]
    while agenda:
        path = agenda.pop(-1)
        val = path[0][-1]
        form = update(val, path[1])
        if form == None: continue # no solution, so backtrack
        sub_path, new_form  = clause_path(form)
        if new_form == None: continue
        new_path = path[0] + sub_path # add one claue tuples to current path
        if new_form == []: return new_path
        val = next(iter(new_form[0]))
        agenda.append([new_path + [val], new_form])
        agenda.append([new_path+[(val[0], not val[1])], new_form])
    return None # return None if no path found

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    
    formula = convert(formula)
    path = dfs(formula)
    if path == {}: return {}
    if path == None: return None
    res = {}
    for val in path:
        res[val[0]] = val[1] # add variables and their corresponding truth values to dicitonary from path
    return res

def only_desired_sessions(student_preferences):
    """
    Parameters
    ----------
    student_preferences : a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    Returns
    -------
    res : a cnf formula that makes sure students are only assigned to rooms in their preferences

    >>> student_preferences = {'Alice': {'basement', 'penthouse'},
    ...                        'Bob': {'kitchen'}}
    >>> res = only_desired_sessions(student_preferences)
    >>> x = convert(res)
    >>> {('Alice_basement', True), ('Alice_penthouse', True)} in x
    True
    >>> {('Bob_kitchen', True)} in x
    True
    """
    res = []
    for student in student_preferences:
        temp = []
        for room in student_preferences[student]: # for each room that the student has a preference for
            temp.append((student + "_" + room, True))
        res.append(temp)
    return res

def room_possibilities(name, rooms):
    """
    Parameters
    ----------
    name : string, name of a student
    rooms : a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns
    -------
    list, of variables corresponding to the student and all available rooms, all with truth value False

    """
    return [(name + "_" + room, False) for room in rooms]

def student_possibilities(room, names):
    """
    Parameters
    ----------
    room: string, name of a room
    names: a dictionary mapping a student name (string) to a set
            of room names (strings) that work for that student

    Returns
    -------
    list, of variables corresponding to the room and all available students, all with truth value False
    
    """
    return [(name + "_" + room, False) for name in names]

def combinations(n, k):
    """
    Produces sublists of a given size, k

    Parameters
    ----------
    n : a list of lists
    k : int, size of sublists needed

    Returns
    -------
    list, containing sublists of given size
    
    >>> combinations(['a', 'b', 'c', 'd'], 3)
    [['c', 'b', 'a'], ['d', 'b', 'a'], ['d', 'c', 'a'], ['d', 'c', 'b']]
    """
    # base cases
    if k == 0:
        return [[]]
    if len(n) == 0:
        return []
    n2 = n[1:] #create copy without first element
    # get sublists of size k - 1 without first element
    subcombs = combinations(n2, k - 1)
    for comb in subcombs:
        comb.append(n[0])
    return subcombs + combinations(n2, k) # add sublists of size k that don't have first element
        
def at_most_one_session(student_preferences, room_capacities):
    """
    Parameters
    ----------
    student_preferences : a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student
    room_capacities : a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns
    -------
    res : a cnf formula that ensures each student must be in at most one room

    >>> student_dict = {'Alice': {'basement', 'penthouse'},
    ...                        'Bob': {'kitchen'}}
    >>> rooms = {'basement': 1, 'penthouse': 4}
    >>> x = convert(at_most_one_session(student_dict, rooms))
    >>> {('Alice_penthouse', False), ('Alice_basement', False)} in x
    True
    >>> {('Bob_penthouse', False), ('Bob_basement', False)} in x
    True
    """
    res = []
    for student in student_preferences:
        possibilities = room_possibilities(student, room_capacities) # variables of all rooms corresponding to that student
        res += combinations(possibilities, 2) # get sublists of size 2
    return res

def no_oversubscribed_sessions(student_preferences, room_capacities):
    """
    Parameters
    ----------
    student_preferences : a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student
    room_capacities : a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns
    -------
    res : a cnf formula that ensures that each room capacity isn't exceeded

    >>> student_dict = {'Alice': {'basement', 'penthouse'},
    ...                 'Bob': {'kitchen'}}
    >>> rooms = {'basement': 1, 'penthouse': 4}
    >>> x = convert(no_oversubscribed_sessions(student_dict, rooms))
    >>> {('Bob_basement', False), ('Alice_basement', False)} in x
    True
    >>> {('Bob_penthouse', False), ('Alice_penthouse', False)} in x
    False
    """
    res = []
    num_students = sum(1 for student in student_preferences) # get number of students
    for room in room_capacities:
        size = room_capacities[room]
        if size >= num_students: continue
        possibilities = student_possibilities(room, student_preferences) # variables of all students corresponding to a room
        res += combinations(possibilities, size + 1) # sublists that ensure size+1 students won't be assigned to a room
    return res

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    return only_desired_sessions(student_preferences) + at_most_one_session(student_preferences, room_capacities) \
        + no_oversubscribed_sessions(student_preferences, room_capacities)


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    
    #doctest.run_docstring_examples(satisfying_assignment, globals(), optionflags=_doctest_flags, verbose=False)

    # formula  = [
    # {('a', True), ('b', True), ('c', True)},
    # {('a', False)},
    # {('d', False), ('e', True), ('a', True), ('g', True)},
    # {('h', False), ('c', True), ('a', False), ('f', True)}]
    # #print(satisfying_assignment(formula))
    # # form = update(('a', True), formula)
    # # print(form)
    # # form = update(('f', False), form)
    # # print(form)
    # # form = update(('h', True), form)
    # # print(form)
    # # form = update(('c', False), form)
    # # print(form)
    # # print(get_elements([[]]))
    # formula2 = [{("a",True), ("b",True)}, {("a",False), ("b",False), ("c",True)},
    #            {("b",True),("c",True)}, {("b",True),("c",False)}]
    # cnf = [[("d",True),("b",True)],[("a",False),("b",True)], [("a",True),("b",False),("c",True)], [("b",True),("c",True)], [("b",True),("c",False)], [("a",True),("b",False),("c",False)]]
    # cnf3 = [[('a', True), ('a', False)], [('b', True), ('a', True)], [('b', True)], [('b', False), ('b', False), ('a', False)], [('c', True), ('d', True)], [('c', True), ('d', True)]]
    # #print(satisfying_assignment(cnf3))
    
    # student_dict = {'Alice': {'basement', 'penthouse'},
    #                         'Bob': {'kitchen'}}
    # rooms = {'basement': 1, 'penthouse': 4}
    # no_oversubscribed_sessions(student_dict, rooms)
    # form = [{('f', True)}, {('h', False), ('c', True), ('f', True)}]
    # print(dfs(formula2))
    # print(only_desired_sessions(student_dict))
    
    # print(combinations(['a', 'b', 'c', 'd'], 3))
#     print(k)

# print(combinations(['a', 'b', 'c', 'd', ], 2))