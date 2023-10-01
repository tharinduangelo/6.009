#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)

    Parameters
    ----------
    nodes_filename : string, of filepath to pickle file containing node information
    ways_filename : string, of filepath to pickle file containing way information

    Returns
    -------
    locations : dict, containing key value pairs of nodes and a set of adjacent nodes (successors)
    geographic_locations : dict, containing key value pairs of node ids and a tuple of coordinates
    speed_limits : dict, containing key value pairs of tuples of adjacent nodes and allowed speed limit
    max_speed : int, of maximum speed across all ways considered
    
    """
    
    locations = {} # initialize dictionary to store key value pairs of nodes and a set of adjacent nodes
    speed_limits = {} # initialize dictionary to store key value pairs of tuples of adjacent nodes and allowed speed limit
    allowed_nodes = set() # keep track of nodes that can be considered
    max_speed = 0
    
    def update_speed_limits(node1, node2):
        """
        adds adjcent node tuples and maximum speed among them to speed_limits dictionary
        """
        if (node1, node2) not in speed_limits or speed_limits[(node1, node2)] < speed:
            speed_limits[(n, node2)] = speed
        
    for way in read_osm_data(ways_filename):
        # check if path is an allowed highway
        if 'highway' not in way['tags'] or way['tags']['highway'] not in ALLOWED_HIGHWAY_TYPES: continue
        node_list = way['nodes'] # get list of nodes in that way
        oneway = False # set flag
        # check if path is oneway
        if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes': oneway = True
        # get speed limit for the way
        speed = way['tags']['maxspeed_mph'] if 'maxspeed_mph' in way['tags'] else DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
        if speed > max_speed: max_speed = speed # update max speed
        # for each node, find adjacent nodes and add them to a set corresponding to that node
        for n in node_list:
            allowed_nodes.add(n)
            n_index = node_list.index(n)
            if n_index + 1 == len(node_list): # if node has no adjacent node to the right
                res = set() 
            else:
                node1 = node_list[n_index + 1] # node after current node
                res = {node1}
                update_speed_limits(n, node1)
            if not oneway and n_index != 0 :
                node2 = node_list[n_index - 1] # node before current node
                res.add(node2) # add previous node if path not oneway
                update_speed_limits(n, node2)
            if n not in locations:
                locations[n] = res
            else:
                locations[n] |= res
    
    geographic_locations = {} # intialize dictionary to store key value pairs of node ids and a tuple of coordinates
    for node in read_osm_data(nodes_filename):
        if node['id'] in allowed_nodes:
            geographic_locations[node['id']] = (node['lat'], node['lon'])

    return locations, geographic_locations, speed_limits, max_speed

def insort(L, x, low):
    """
    Insert item x into a list L sorted from L[low:], and keep it sorted.

    """
    hi = len(L)
    while low < hi:
        mid = (low+hi)//2
        if x < L[mid]:
            hi = mid
        else:
            low = mid+1
    L.insert(low, x)

def fastest_or_shortest_path_nodes(aux_structures, node1, node2, category):
    
    """
    Returns the shortest or fastest path between two nodes

    Parameters
    ----------
    aux_structures: the result of calling build_auxiliary_structures
    node1: int, node representing the start location
    node2: int, node representing the end location
    category : string, "shortest" if you want shortest path, "fastest" if you want fastest path

    Returns
    -------
    list, of nodes corresponding to shortest or fastest path
    None, if no path found
    """
    
    # Uniform cost search
    terminal_loc = aux_structures[1][node2]
    # initialize a list to keep track of tuple pairs of paths and their associated costs that have yet to be considered
    agenda = [(0, [node1], 0)] # (heurtistic cost, path, actual cost)
    extended = set() # a set to store nodes that we have already expanded
    # count = 0
    pointer = 0 # initialize pointer to keep track of sublist of agenda to be considered
    while pointer < len(agenda):
        path = agenda[pointer] # get first element of sublist of agenda
        pointer += 1
        # count += 1
        terminal_vertex = path[1][-1] # get the last vertex of current path
        if terminal_vertex in extended: continue 
        if terminal_vertex == node2: 
            # print("count =", count)
            return path[1] # return path if already found
        extended.add(terminal_vertex) 
        for child in aux_structures[0][terminal_vertex]: # get the adjacent nodes of terminal vertex
            if child not in extended:
                new_path = path[1] + [child]
                if category == "shortest":
                    # calculate cost of new path and heuristic cost
                    new_cost = path[2] + great_circle_distance(aux_structures[1][terminal_vertex], aux_structures[1][child])
                    # heuritic: Euclidean distance
                    new_heuristic_cost = new_cost + great_circle_distance(aux_structures[1][child], terminal_loc)
                else:
                    new_cost = path[2] + great_circle_distance(aux_structures[1][terminal_vertex], aux_structures[1][child]) / \
                        aux_structures[2][(terminal_vertex, child)]
                    # heuristic: Euclidean distance / max_speed
                    new_heuristic_cost = new_cost + great_circle_distance(aux_structures[1][child], terminal_loc) / aux_structures[3]
                # add new path keeping agenda sorted
                insort(agenda, (new_heuristic_cost, new_path, new_cost), pointer)
    return None # return None if no path found

def find_short_path_nodes(aux_structures, node1, node2):
    
    """
    Return the shortest path between the two nodes

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: int, node representing the start location
        node2: int, node representing the end location

    Returns:
        list, of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    
    return fastest_or_shortest_path_nodes(aux_structures, node1, node2, "shortest")


def shortest_distance_node(aux_structures, loc):
    
    """
    Returns the node closest to a given location

    Parameters
    ----------
    aux_structures : the result of calling build_auxiliary_structures
    loc : tuple, of latitutude and longitude coordinates

    Returns
    -------
    closest_node : TYPE
        DESCRIPTION.

    """
    shortest_distance = float('inf') # initialize minimum distance
    for node_id in aux_structures[1]:
        # get distance between node and location considered
        distance = great_circle_distance(loc, aux_structures[1][node_id])
        if distance < shortest_distance:
            shortest_distance = distance
            closest_node = node_id
    return closest_node

def find_short_or_fast_path(aux_structures, loc1, loc2, category):
    
    """
    Find shortest or fastest path between two points

    Parameters
    ----------
    aux_structures : the result of calling build_auxiliary_structures
    loc1 : tuple, of latitutude and longitude coordinates of start location
    loc2 : tuple, of latitutude and longitude coordinates of end location
    category : string, "shortest" if you want shortest path, "fastest" if you want fastest path

    Returns
    -------
    list, of tuples containing locations of nodes in path found
    None, if no path found

    """
    
    start_node = shortest_distance_node(aux_structures, loc1)
    end_node = shortest_distance_node(aux_structures, loc2)
    path = fastest_or_shortest_path_nodes(aux_structures, start_node, end_node, category)
    if path == None: return None
    return [aux_structures[1][node] for node in path]
                
def find_short_path(aux_structures, loc1, loc2):
    
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    return find_short_or_fast_path(aux_structures, loc1, loc2, "shortest")

def find_fast_path(aux_structures, loc1, loc2):
    
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    
    return find_short_or_fast_path(aux_structures, loc1, loc2, "fastest")


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    # print(sum(1 for node in read_osm_data('resources/cambridge.nodes')))
    # print(sum(1 for node in read_osm_data('resources/cambridge.nodes') if 'name' in node['tags']))
    # for node in read_osm_data('resources/cambridge.nodes'):
    #     if node['tags'].get('name', '0') == '77 Massachusetts Ave':
    #         print(node['id'])
    #         break
    # print(sum(1 for way in read_osm_data('resources/cambridge.ways')))
    # print(sum(1 for way in read_osm_data('resources/cambridge.ways') if way['tags'].get('oneway', 'no') == 'yes'))

    # print(great_circle_distance((42.363745, -71.100999),(42.361283, -71.239677)))
    # for node in read_osm_data('resources/midwest.nodes'):
    #     if node['id'] == 233941454: a = (node['lat'], node['lon'])
    #     if node['id'] == 233947199: b = (node['lat'], node['lon'])
    # print(great_circle_distance(a, b))
    
    # for way in read_osm_data('resources/midwest.ways'):
    #     if way['id'] == 21705939: 
    #         nodes = way['nodes']
    #         break
        
    # coordinates = [(n['lat'], n['lon']) for n in read_osm_data('resources/midwest.nodes') if n['id'] in nodes]
    
    # distance = 0
    # for i in range(len(coordinates)-1): distance += great_circle_distance(coordinates[i], coordinates[i+1])
    # print(distance)
    
    # aux_structures = build_auxiliary_structures('resources/midwest.nodes', 'resources/midwest.ways')
    # node_id = shortest_distance_node(aux_structures, (41.4452463, -89.3161394))
    # print(node_id)
    
    # aux_structures = build_auxiliary_structures('resources/cambridge.nodes', 'resources/cambridge.ways')
    # find_short_path(aux_structures, (42.3858, -71.0783), (42.5465, -71.1787))
    # with heuristic, count = 47501
    # without heuristic, count = 385742
    # find_short_or_fast_path(aux_structures, (42.3858, -71.0783), (42.5465, -71.1787), "fastest")
    # with heuristic, count = 82328
    # without heuristic, count = 291020

    # phs = (41.375288, -89.459541)
    # timber_edge = (41.452802, -89.443683)
    # aux = build_auxiliary_structures('resources/midwest.nodes', 'resources/midwest.ways')
    # print(to_local_kml_url(find_short_path(aux, phs, timber_edge)))
    pass