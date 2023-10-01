#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 13:42:24 2021

@author: Tharindu
"""

#     # Uniform cost search
#     terminal_loc = aux_structures[1][node2]
#     agenda = {((node1,), 0)} # a set to keep track of tuple pairs of paths and their associated times that have yet to be considered
#     extended = set() # a set to store nodes that we have already expanded
#     #count = 0
#     while agenda:
#         if category == "shortest":
#             # get the path with the mininimum distance + a heuristic function: great_circle_distance(n,goal)
#             path = min(agenda, key = lambda t: t[1] + great_circle_distance(aux_structures[1][t[0][-1]], terminal_loc))
#         else:
#             # get the path with the mininimum time
#             path = min(agenda, key = lambda t: t[1])
#         agenda.remove(path)
#         #count += 1
#         terminal_vertex = path[0][-1] # get the last vertex of current path
#         if terminal_vertex in extended: continue 
#         if terminal_vertex == node2: 
#             #print("count =", count)
#             return list(path[0]) # return path if already found
#         extended.add(terminal_vertex) 
#         for child in aux_structures[0][terminal_vertex]: # get the adjacent nodes of terminal vertex
#             if child not in extended:
#                 new_path = path[0] + (child,)
#                 if category == "shortest":
#                     # calculate cost of new path
#                     new_cost = path[1] + great_circle_distance(aux_structures[1][terminal_vertex], aux_structures[1][child])
#                 else:
#                     new_cost = path[1] + \
# great_circle_distance(aux_structures[1][terminal_vertex], aux_structures[1][child]) / aux_structures[2][(terminal_vertex, child)]
#                 agenda.add((new_path, new_cost))
#     return None # return None if no path found
