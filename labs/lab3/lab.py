#!/usr/bin/env python3
# Name: Tharindu Withanage
# Collaborators: None

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).

Kevin_Bacon_ID = 4724

def transform_data(raw_data):
    
    """
    Parameters
    ----------
    raw_data : list, containing 3-tuples of the form (actor ID 1, actor ID 2), movie ID
                of film they acted in

    Returns
    -------
    a tuple, of the form (actors, movies1, movies2
                          )
    actors : a dict with key value pairs corresponding to an actor ID, and the set of actors the actor acted with
    movies1 : a dict with key value pairs corresponding to a tuple of actor IDs, and the movie they acted in
    movies2 : a dict with key value pairs corresponding to a movie ID, and the set of actors who acted in it
    
    """
    
    actors = {}
    movies1 = {}
    movies2 = {}
    for pair in raw_data:
        for i in range(2): # to get actor1 and actor2 IDs
            if pair[i] not in actors:
                actors[pair[i]] = {pair[(i + 1) % 2]}
            else:
                actors[pair[i]].add(pair[(i + 1) % 2])
            movies1[(pair[i],pair[(i + 1) % 2])] = pair[2]
        if pair[2] not in movies2:
            movies2[pair[2]] = {pair[0], pair[1]}
        else:
            movies2[pair[2]].add(pair[0])
            movies2[pair[2]].add(pair[1])
            
    return (actors, movies1, movies2)

def acted_together(data, actor_id_1, actor_id_2):
    
    """
    Parameters
    ----------
    data : 3-tuple of transformed raw data
    actor_id_1 : int, ID of actor 1
    actor_id_2 : int, ID of actor 2

    Returns
    -------
    bool, True if they acted together, False otherwise

    """
    
    if actor_id_1 == actor_id_2: return True
    if actor_id_1 in data[0]:
        if actor_id_2 in data[0][actor_id_1]: return True
    return False
    

def actors_with_bacon_number(data, n):
    
    """

    Parameters
    ----------
    data : 3-tuple of transformed raw data
    n : int, corresponding to the bacon number we want actors to have

    Returns
    -------
    set, of actor IDs corresponding to actors who have that bacon number

    """
    
    if n == 0: return {Kevin_Bacon_ID}
    
    agenda = [Kevin_Bacon_ID] # initialize list to store actors with a particular bacon number
    visited = {Kevin_Bacon_ID} # initialize set to store actors that have already been seen
    for i in range(n):
        temp = []
        for x in agenda:
            for child in data[0][x]: # get actors who worked with each actor in agenda
                if child not in visited:
                    temp.append(child)
                    visited.add(child)
        agenda = temp # update agenda to now have actors with one higher bacon number
        if agenda == []: return set()
    return set(agenda)

    
def bacon_path(data, actor_id):
    
    """
    
    Parameters
    ----------
    data : 3-tuple of transformed raw data
    actor_id : int, actor ID

    Returns
    -------
    list, path of actors from Kevin Bacon to actor in question
    None, if no path found

    """
    
    return actor_to_actor_path(data, Kevin_Bacon_ID, actor_id)


def actor_to_actor_path(data, actor_id_1, actor_id_2):
    
    """
    
    Parameters
    ----------
    data : 3-tuple of transformed raw data
    actor_id_1 : int, actor ID of actor 1
    actor_id_2 : int, actor ID of actor 2

    Returns
    -------
    list, path of actors from actor 1 to actor 2
    None, if no path found

    """
    
    return actor_path(data, actor_id_1, lambda p: p == actor_id_2)
    

def movie_path(data, actor_id_1, actor_id_2):
    
    """
    
    Parameters
    ----------
    data : 3-tuple of transformed raw data
    actor_id_1 : int, actor ID of actor 1
    actor_id_2 : int, actor ID of actor 2

    Returns
    -------
    list, path of movies from actor 1 to actor 2
    None, if no path found

    """
    
    actors = actor_to_actor_path(data, actor_id_1, actor_id_2) # get actor path
    
    if actors == None: return None
    
    return [data[1][(actors[i], actors[i + 1])] for i in range(len(actors)-1)] # get movie path
        
    
def actor_path(data, actor_id_1, goal_test_function):
    
    """
    
    Parameters
    ----------
    data : 3-tuple of transformed raw data
    actor_id_1 : int, actor ID of actor 1
    goal_test_function : function, that takes in one actor ID and returns True if actor represents a valid
                        ending location for the path, False otherwise

    Returns
    -------
    list, path of actors from actor 1 to actor 2, where actor 2 returns True when passed into the goal_test_function
    None, if no path found

    """
    
    if goal_test_function(actor_id_1): return [actor_id_1] # starting actor satisfies goal test function
    
    # find path using breadth first search
    
    agenda = [[actor_id_1]] # initialize list that will store paths to be considered
    visited = {actor_id_1} # initialize set that contains actors that have already been seen
    pointer = 0
    while pointer < len(agenda):
        current_path = agenda[pointer] # get the path at start of list
        pointer += 1
        terminal_vertex = current_path[-1] # get last actor of current path
        
        for child in data[0][terminal_vertex]: # get actors who worked with current actor
            new_path = current_path + [child] 
            if goal_test_function(child): # check if new actor satisfies terminating condition
                return new_path
            elif child not in visited:
                agenda.append(new_path)
                visited.add(child)
    
    return None # return None if no path found

def actors_connecting_films(data, film1, film2):
    
    """
    
    Parameters
    ----------
    data : 3-tuple of transformed raw data
    film1 : int, movie ID of film 1
    film2 : int, movie ID of film 2

    Returns
    -------
    list, path of actors connecting film 1 to film 2
    None, if no path found

    """
    
    length = float('inf') # set length of result list to infinity
    changed = False # initialize a flag to False to check if path will be found
    film1_actors = data[2][film1]
    film2_actors = data[2][film2]
    for actor1 in film1_actors:
        temp = actor_path(data, actor1, lambda p: p in film2_actors) # get path from actor1 to actor2
        if temp is not None and len(temp) < length:
            res = temp # update shortest path
            length = len(res) # update shortest path length
            changed = True # update flag
    if changed:
        return res
    return None # return None if path not found

if __name__ == '__main__':
    # with open('resources/small.pickle', 'rb') as f:
    #     smalldb = pickle.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    # with open('resources/names.pickle', 'rb') as f1:
    #     names = pickle.load(f1)
    # print(type(names))
    # for key, value in names.items():
    #     print([key, value])
    #     break
    # print(names['Katarina Bistrovic-Darvas'])
    # print(list(names.keys())[list(names.values()).index(1860)])

    # with open('resources/names.pickle', 'rb') as f:
    #     names = pickle.load(f)
    # with open('resources/small.pickle', 'rb') as f:
    #     smalldb = pickle.load(f)
    # data = transform_data(smalldb)
    # print(acted_together(data, names['Jason Robards'], names['Stanley Tucci']))
    # print(acted_together(data, names['Jeff Perry'], names['Rose Byrne']))
        
    # with open('resources/large.pickle', 'rb') as f:
    #     largedb = pickle.load(f)
    # with open('resources/names.pickle', 'rb') as f:
    #     names = pickle.load(f)
    # actors = actors_with_bacon_number(transform_data(largedb), 6)
    # res = set()
    # for i in actors:
    #     res.add(list(names.keys())[list(names.values()).index(i)])
    # print(res)
    
    # with open('resources/large.pickle', 'rb') as f:
    #     large = pickle.load(f)
    
    # with open('resources/names.pickle', 'rb') as f:
    #     names = pickle.load(f)
        
    # with open('resources/movies.pickle', 'rb') as f:
    #     movies = pickle.load(f)
        
    # ids = bacon_path(transform_data(large), names['Billie Brockwell'])
    # print([list(names.keys())[list(names.values()).index(i)] for i in ids])
    
    # ids = actor_to_actor_path(transform_data(large), names['Jun Tatara'], names['Dan Fogelman'])
    # print([list(names.keys())[list(names.values()).index(i)] for i in ids])
    
    # movie_ids = movie_path(transform_data(large), names['Ron Howard'], names['Vjeran Tin Turk'])
    # print([list(movies.keys())[list(movies.values()).index(i)] for i in movie_ids])
    pass