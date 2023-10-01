#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 16:58:38 2021

@author: Tharindu
"""

def sub_list_empty(formula):
    return any(k == set() for k in formula)

def update(val, formula):
    res = set()
    for sub_set in formula:
        if val in sub_set: continue
        res.add({x for x in sub_set if x[0] != val[0]})
    return res

def unit_clauses(formula):
    return {k[0]:k[1] for sub_set in formula for k in sub_set if len(sub_set) == 1}

def get_clause(formula):
    for k in formula:
        if len(k) == 1: return k
def get_clause_path(formula):
    res=[]
    while
    
def convert(formula):
    return [set(k) for k in formula]

def get_elements(formula):
    return {i[0] for k in formula for i in k}

def new_dfs(formula):
    suc = get_elements(formula)
    return

def dfs(formula):
    suc = get_elements(formula)
    if suc == set(): return {}
    val = suc.pop()
    clause = unit_clauses(formula)
    if val in clause:
        agenda = [[[(val, clause[val])], formula]]
    else:
        agenda = [[[(val, True)], formula],[[(val, False)], formula]]
    while agenda:
        #print([k[0] for k in agenda])
        #print(count)
        path = agenda.pop(-1)
        val = path[0][-1]
        new_form = update(val, path[1])
        #print(new_form)
        #if new_form == path[1]: continue
        #print(new_form)
        if sub_list_empty(new_form): continue
        if new_form == []: return path[0]
        unit_clause_set = unit_clauses(new_form)
        for k in unit_clause_set:
            agenda.append([path[0] + [(k, unit_clause_set[k])],new_form])
        for neighbor in get_elements(new_form) - set(unit_clause_set.keys()):
            agenda.append([path[0] + [(neighbor, True)],new_form])
            agenda.append([path[0] + [(neighbor, False)],new_form])
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