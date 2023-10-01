#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 01:00:33 2021

@author: Tharindu
"""

def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    
    # if len(pattern) == 1:
    #     if pattern == "*":
    #         return [key for key in trie]
    #     if pattern == "?":
    #         return [key for key in trie if len(key[0]) == 1]
    #     return [key for key in trie if key[0] == pattern]
    if len(pattern) == 0:
        return [key for key in trie]
    if pattern[0] == "*":
        res = []
        res += word_filter(trie, pattern[1:])
        for v in trie.children.values():
            res += word_filter(v, pattern[1:])
            res += word_filter(v, pattern)
        return res
    if pattern[0] == "?":
        res = []
        for k, v in trie.children.items():
            res1 = word_filter(v, pattern[1:])
            res += [(k + key[0], key[1]) for key in res1]
            res += word_filter(v, pattern)
        return res
    res = []
    for k, v in trie.children.items():
        if k == pattern[0]:
            res1 = word_filter(v, pattern[1:])
            res += [(k + key[0], key[1]) for key in res1]
        res += word_filter(v, pattern)
    return res