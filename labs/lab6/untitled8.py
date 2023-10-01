#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 12:43:21 2021

@author: Tharindu
"""

def sub_list_empty(formula):
    return any(k == [] for k in formula)

def update(val, formula):
    res = []
    for sub_list in formula:
        if val in sub_list: continue
        res.append([x for x in sub_list if x[0] != val[0]])
    return res

def unit_clauses(formula):
    return {sub_list[0][0]:sub_list[0][1] for sub_list in formula if len(sub_list) == 1}


def get_elements(formula):
    return {i[0] for k in formula for i in k}

def dfs(formula):
    suc = get_elements(formula)
    if suc == set(): return {}
    val = suc.pop()
    clause = unit_clauses(formula)
    if val in clause:
        agenda = [[[(val, clause[val])], formula]]
    else:
        agenda = [[[(val, True)], formula],[[(val, False)], formula]]
    count = 0
    while agenda and count < 100:
        #print([k[0] for k in agenda])
        #print(count)
        count += 1
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