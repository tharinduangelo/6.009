#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 13 08:06:59 2021

@author: Tharindu
"""

def combinations(n, k):

    # base cases
    if k == 0:
        yield set()
    elif len(n) == 0:
        return
    else:
        n2 = n[1:] #create copy without first element
        # get sublists of size k - 1 without first element
        for comb in combinations(n2, k - 1):
            yield comb | {n[0]}
        for comb in combinations(n2, k):
            yield comb
            
for x in combinations(['a', 'b', 'c', 'd', 'e'], 2):
    print(x)