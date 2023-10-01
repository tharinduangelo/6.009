#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 13:54:28 2021

@author: Tharindu
"""

def char_insertion(trie, word):
    res = []
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for char in alphabet:
        for i in range(len(word)):
            temp = word[:i]+char+word[i:]
            if temp in trie: res.append(temp)
    return res

def char_deletion(trie, word):
    res = []
    for i in range(len(word)):
        temp = word[:i] + word[i + 1:]
        if temp in trie: res.append(temp)
    return res

def char_replacement(trie, word):
    res = []
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(word)):
        for char in alphabet:
            temp = word[:i] + char + word[i + 1:]
            if temp in trie: res.append(temp)
    return res

def two_char_transpose(trie, word):
    res = []
    for i in range(len(word) - 1):
        temp = word[:i] + word[i + 1] + word[i] + word[i + 2:]
        if temp in trie: res.append(temp)
    return res