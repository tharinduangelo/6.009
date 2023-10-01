#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def convert(formula):
    return [set(k) for k in formula]

def sub_list_empty(formula):
    return any(sub_set == set() for sub_set in formula)

def update(val, formula, elements):
    res = []
    not_val = (val[0], not val[1])
    for sub_set in formula:
        if val in sub_set: elements -= sub_set
        elif not_val in sub_set:
            x = sub_set.copy()
            x.remove(not_val)
            res.append(x)
            elements |= x
            # res.append({x for x in sub_set if x != not_val})
        else:
            res.append(sub_set)
    return (res, elements)

def unit_clauses(formula):
    return {sub_list[0][0]:sub_list[0][1] for sub_list in formula if len(sub_list) == 1}

def get_clause(formula):
    for sub_set in formula:
        if len(sub_set) == 1: return list(sub_set)[0]
    return None

def clause_path(formula, elements):
    agenda = []
    clause = get_clause(formula)
    if clause == None: return ([], formula, elements)
    while clause:
        agenda.append(clause)
        formula, elements = update(clause, formula, elements)
        clause = get_clause(formula)
    return (agenda, formula, elements)

def get_elements(formula):
    return {i for k in formula for i in k}

def dfs(formula):
   
    if formula == []: return {}
    if sub_list_empty(formula): return None
    elements = get_elements(formula)
    path, form, elements = clause_path(formula, elements)
    if form == []: return path
    if sub_list_empty(form): return None
    # suc = get_elements(form)
    val = elements.pop()
    agenda = [[path + [val], form, elements]]
    count = 0
    # print(agenda)
    while agenda and count < 1000:
        # print([k[0] for k in agenda])
        count += 1
        path = agenda.pop(-1)
        val = path[0][-1]
        form, elements = update(val, path[1], path[2])
        if sub_list_empty(form): continue
        if form == []: return path[0]
        l, new_form, elements  = clause_path(form, elements)
        new_path = path[0] + l
        if sub_list_empty(new_form): continue
        if new_form == []: return new_path
        for neighbor in elements:
            agenda.append([new_path + [neighbor],new_form, elements])
            # agenda.append([new_path + [(neighbor, False)],new_form])
    return None

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
        res[val[0]] = val[1]
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
    raise NotImplementedError


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags)
    
    doctest.run_docstring_examples(satisfying_assignment, globals(), optionflags=_doctest_flags, verbose=False)

    formula  = [
    [('a', True), ('b', True), ('c', True)],
    [('a', False), ('f', True)],
    [('d', False), ('e', True), ('a', True), ('g', True)],
    [('h', False), ('c', True), ('a', False), ('f', True)],
]
    #print(satisfying_assignment(formula))
    # form = update(('a', True), formula)
    # print(form)
    # form = update(('f', False), form)
    # print(form)
    # form = update(('h', True), form)
    # print(form)
    # form = update(('c', False), form)
    # print(form)
    # print(get_elements([[]]))
    formula = [[("a",True), ("b",True)], [("a",False), ("b",False), ("c",True)],
               [("b",True),("c",True)], [("b",True),("c",False)]]
    cnf = [[("d",True),("b",True)],[("a",False),("b",True)], [("a",True),("b",False),("c",True)], [("b",True),("c",True)], [("b",True),("c",False)], [("a",True),("b",False),("c",False)]]
    print(satisfying_assignment(cnf))