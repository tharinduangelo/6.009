#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, set): continue
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'bombs': {(0, 0), (1, 0), (1, 1)},
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'bombs': {(0, 0), (1, 0), (1, 1)},
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """
    return dig_nd(game, (row, col))
    

def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'bombs': {(0, 0), (1, 0), (1, 1)},
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'bombs': {(0, 0), (1, 0), (1, 1)},
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)


def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'bombs': {(0, 0), (1, 0), (1, 1)},
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    return '\n'.join([''.join(i) for i in render_2d(game, xray)])



# N-D IMPLEMENTATION
def first_coord_valid(dim, location):
    """
    Returns True if the first coordinate of a given location falls within first board dimension, False otherwise
    
    >>> first_coord_valid((2,3,4), (2,1,3))
    False
    >>> first_coord_valid((9, 7), (7, 5))
    True
    """
    return 0 <= location[0] < dim[0]
        
    
def valid_neighbors(dim, loc):
    """
    Parameters
    ----------
    dim : tuple of dimensions of board
    loc : tuple of coordinates of location

    Returns
    -------
    a generator object that provides all valid neighbors of location including location when iterated
    
    >>> {i for i in valid_neighbors((2, 3), (1,1))} == {(0, 1), (1, 2), (0, 0), (1, 1), (0, 2), (1, 0)}
    True
    >>> {i for i in valid_neighbors((3, 5), (2, 4))} == {(2, 3), (2, 4), (1, 3), (1, 4), (3, 4)}
    False
    """
    
    # base case
    if len(loc) == 1:
        for i in range(-1, 2):
            neighbor = (loc[0] + i,)
            #check if location within board
            if first_coord_valid(dim, neighbor): yield neighbor
    # recursive case
    else:
        for sub_combinations in valid_neighbors(dim[1:], loc[1:]):
            for i in range(-1, 2):
                neighbor = (loc[0] + i,) + sub_combinations
                # check if location within board
                if first_coord_valid(dim, neighbor): yield neighbor


def get_value(board, loc):
    """
    Return value of coordinate: loc on board
    
    >>> get_value([[1, 0, 2], [0, 1, 3]], (1, 2))
    3
    """
    if len(loc) == 1: return board[loc[0]]
    return get_value(board[loc[0]],loc[1:])

def set_value(board, loc, val):
    """ 
    Set the value of board at coordinate: loc to value: val
    
    >>> board = [[3, 4], [6, 7]]
    >>> set_value(board, (1, 0), 9)
    >>> board
    [[3, 4], [9, 7]]
    """
    if len(loc) == 1:
        board[loc[0]] = val
    else: 
        set_value(board[loc[0]],loc[1:], val)
    
def update_value(board, loc, val):
    """ 
    Updates value at board location loc by adding val
    
    >>> board = [[6, 9, 5], [2, 3, 4]]
    >>> update_value(board, (0, 1), 7)
    >>> board
    [[6, 16, 5], [2, 3, 4]]
    """
    if len(loc) == 1:
        board[loc[0]] += val
    else:
        update_value(board[loc[0]],loc[1:], val)

def grid(dim, val):
    """
    Creates and returns an nd list of given dimensions, dim (tuple) filled with a given value, val
        
    >>> grid((2, 3), 0)
    [[0, 0, 0], [0, 0, 0]]
    """
    if len(dim) == 1: # base case
        return [val for i in range(dim[0])]
    # recursive case
    return [grid(dim[1:], val) for i in range(dim[0])]
    

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    
    board = grid(dimensions, 0)
    mask = grid(dimensions, False)
    
    bomb_set = set(bombs)
    
    for loc in bombs: 
        set_value(board, loc, '.')
        for n in valid_neighbors(dimensions, loc):
            if n in bomb_set: continue
            update_value(board, n, 1)

    return {
        'dimensions': dimensions,
        'board' : board,
        'mask' : mask,
        'bombs': bomb_set,
        'state': 'ongoing'}

def num_locs(dim):
    """
    Returns total number of possible locations given board dimensions
    
    >>> num_locs((5,4,2))
    40
    """
    prod = 1
    for d in dim: prod *= d
    return prod

def mask_sum(mask):
    """
    Return the number of locations in mask that have the value True
    >>> mask = [[False, True, True], [False, False, True]]
    >>> mask_sum(mask)
    3
    """
    if isinstance(mask[0], bool): return sum(mask)

    return sum(mask_sum(sub_list) for sub_list in mask)

def dig_nd(game, coordinates, rem_safe_loc = None):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging
       rem_safe_loc: list containing number of safe locations (tuples)

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'bombs': {(1, 0, 0), (0, 0, 1), (1, 1, 1)},
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'bombs': {(1, 0, 0), (0, 0, 1), (1, 1, 1)},
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """   

    if get_value(game['mask'], coordinates) == True: return 0 # if already visited
    set_value(game['mask'], coordinates, True) # change mask value to visible
    current_board = get_value(game['board'], coordinates)
    if current_board == '.':
        game['state'] = 'defeat'
        return 1
    
    # initialize number of remaining safe locations
    if rem_safe_loc == None:
        rem_safe_loc = [num_locs(game['dimensions']) - len(game['bombs']) - mask_sum(game['mask'])+1]
    
    rem_safe_loc[0] -= 1 # update number of remaining safe locations
    if rem_safe_loc[0] == 0: game['state'] = 'victory'
    
    if current_board != 0: return 1

    # if current board value == 0
    count = 1
    for n in valid_neighbors(game['dimensions'], coordinates): # get neighbors
        if n not in game['bombs']:
            count += dig_nd(game, n, rem_safe_loc) # update count
    return count

def boards(board,mask, dim, xray):
    """
    Create a board ready for display
    """
    if len(dim) == 1: # base case
        return ['_' if not xray and not k else ' ' if i == 0 else str(i) for i,k in zip(board, mask)]
    # recursive case
    return [boards(l, m, dim[1:], xray) for l, m in zip(board, mask)]


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'bombs': {(0, 0, 1), (1, 0, 0), (1, 1, 1)},
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    
    return boards(game['board'], game['mask'], game['dimensions'], xray)


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
    #doctest.run_docstring_examples(render_ascii, globals(), optionflags=_doctest_flags, verbose=False)
    #doctest.run_docstring_examples(new_game_2d, globals(), optionflags=_doctest_flags, verbose=False)
    doctest.run_docstring_examples(dig_2d, globals(), optionflags=_doctest_flags, verbose=False)
    #doctest.run_docstring_examples(mask_sum, globals(), optionflags=_doctest_flags, verbose=False)