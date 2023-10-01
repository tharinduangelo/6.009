#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 19:47:34 2021

@author: Tharindu
"""

def match(word, pattern):
    if len(word) == 0 or len(pattern) == 1:
        if pattern == "*":
            return True
        if pattern == "?":
            return len(word) == 1
        return word == pattern
    if pattern[0] == "*":
        return any(match(word[i:], pattern[1:]) for i in range(len(word)))
    if pattern[0] == "?":
        return match(word[1:], pattern[1:])
    if pattern[0] != word[0]:
        return False
    return match(word[1:], pattern[1:])
    
def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    return [key for key in trie if match(key[0], pattern)]

    # trie.keyType(prefix) # check if prefix has correct type
    # flag = False # flag to keep track of whether max_count is None or not
    # if max_count != None: flag = True
    # res = [] # list to store results
    # if prefix in trie:
    #     if flag:
    #         res.append((prefix, trie[prefix]))
    #     else: res.append(prefix)
    # trie2 = trie.get_trie(prefix) # get trie node corresponding to last 
    # if len(prefix) == 0: trie2 = trie
    # for k, v in trie2:
    #     if flag:
    #         res.append((prefix + k, v))
    #     else: res.append(prefix + k)
    # if flag:
    #     sorted_list = sorted(res, key = lambda x : x[1])
    #     res = []
    #     while sorted_list and len(res) < max_count:
    #         res.append(sorted_list.pop()[0])
    # return res


