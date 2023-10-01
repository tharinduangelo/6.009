#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def valid_locations2(num_rows, num_cols):
    """
    Returns all valid locations given board dimensions
    """
    return {(i, j) for j in range(num_cols) for i in range(num_rows)}

def neighbors(loc, num_rows, num_cols):
    """
    Get neighboring locations of a given location that are within the board
    """
    all_neighbors = {(loc[0] + i, loc[1] + j) for i in range(-1, 2) for j in range(-1, 2)}-{loc}
    return all_neighbors & valid_locations2(num_rows, num_cols)


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
    
    bomb_set = set(bombs)
    board = [['.' if (i,j) in bomb_set else 0 for j in range(num_cols)] for i in range(num_rows)]
    # board = []
    # for r in range(num_rows):
    #     row = []
    #     for c in range(num_cols):
    #         if [r,c] in bombs or (r,c) in bombs:
    #             row.append('.')
    #         else:
    #             row.append(0)
    #     board.append(row)
    mask = [[False for j in range(num_cols)] for i in range(num_rows)]
    # mask = []
    # for r in range(num_rows):
    #     row = []
    #     for c in range(num_cols):
    #         row.append(False)
    #     mask.append(row)
    
    for bomb in bombs:
        for n in neighbors(bomb, num_rows, num_cols):
            if n in bomb_set: continue
            board[n[0]][n[1]] += 1
            
    # for r in range(num_rows):
    #     for c in range(num_cols):
    #         if board[r][c] == 0:
    #             neighbor_bombs = 0
    #             if 0 <= r-1 < num_rows:
    #                 if 0 <= c-1 < num_cols:
    #                     if board[r-1][c-1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r < num_rows:
    #                 if 0 <= c-1 < num_cols:
    #                     if board[r][c-1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r+1 < num_rows:
    #                 if 0 <= c-1 < num_cols:
    #                     if board[r+1][c-1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r-1 < num_rows:
    #                 if 0 <= c < num_cols:
    #                     if board[r-1][c] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r < num_rows:
    #                 if 0 <= c < num_cols:
    #                     if board[r][c] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r+1 < num_rows:
    #                 if 0 <= c < num_cols:
    #                     if board[r+1][c] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r-1 < num_rows:
    #                 if 0 <= c+1 < num_cols:
    #                     if board[r-1][c+1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r < num_rows:
    #                 if 0 <= c+1 < num_cols:
    #                     if board[r][c+1] == '.':
    #                         neighbor_bombs += 1
    #             if 0 <= r+1 < num_rows:
    #                 if 0 <= c+1 < num_cols:
    #                     if board[r+1][c+1] == '.':
    #                         neighbor_bombs += 1
    #             board[r][c] = neighbor_bombs
    return {
        'dimensions': (num_rows, num_cols),
        'board' : board,
        'mask' : mask,
        'state': 'ongoing'}


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

    # if game['state'] == 'defeat' or game['state'] == 'victory':
    #     return 0 # keep the state the same

    if game['mask'][row][col] == True:
        return 0
    game['mask'][row][col] = True
    board_width = game['dimensions'][0]
    board_height = game['dimensions'][1]
    bomb_set = {(i, j) for j in range(board_height) for i in range(board_width) if game['board'][i][j] == '.'}
    non_bomb_loc = valid_locations2(board_width, board_height) - bomb_set
    if all(game['mask'][loc[0]][loc[1]] for loc in non_bomb_loc):
        game['state'] = 'victory'
        return 1
    if game['board'][row][col] == '.':
        game['state'] = 'defeat'
        return 1
    if game['board'][row][col] != 0:
        return 1
    
    count = 1
    for n in neighbors((row, col), board_width, board_height):
        if n not in bomb_set:
            count += dig_2d(game, n[0], n[1])
    return count

    # bombs = 0
    # covered_squares = 0
    # for r in range(game['dimensions'][0]):
    #     for c in range(game['dimensions'][1]):
    #         if game['board'][r][c] == '.':
    #             if  game['mask'][r][c] == True:
    #                 bombs += 1
    #         elif game['mask'][r][c] == False:
    #             covered_squares += 1
    # if bombs != 0:
    #     # if bombs is not equal to zero, set the game state to defeat and
    #     # return 0
    #     game['state'] = 'defeat'
    #     return 0
    # if covered_squares == 0:
    #     game['state'] = 'victory'
    #     return 0

    # if game['mask'][row][col] != True:
    #     game['mask'][row][col] = True
    #     revealed = 1
    # else:
    #     return 0

    # if game['board'][row][col] == 0:
    #     num_rows, num_cols = game['dimensions']
    #     if 0 <= row-1 < num_rows:
    #         if 0 <= col-1 < num_cols:
    #             if game['board'][row-1][col-1] != '.':
    #                 if game['mask'][row-1][col-1] == False:
    #                     revealed += dig_2d(game, row-1, col-1)
    #     if 0 <= row < num_rows:
    #         if 0 <= col-1 < num_cols:
    #             if game['board'][row][col-1] != '.':
    #                 if game['mask'][row][col-1] == False:
    #                     revealed += dig_2d(game, row, col-1)
    #     if 0 <= row+1 < num_rows:
    #         if 0 <= col-1 < num_cols:
    #             if game['board'][row+1][col-1] != '.':
    #                 if game['mask'][row+1][col-1] == False:
    #                     revealed += dig_2d(game, row+1, col-1)
    #     if 0 <= row-1 < num_rows:
    #         if 0 <= col < num_cols:
    #             if game['board'][row-1][col] != '.':
    #                 if game['mask'][row-1][col] == False:
    #                     revealed += dig_2d(game, row-1, col)
    #     if 0 <= row < num_rows:
    #         if 0 <= col < num_cols:
    #             if game['board'][row][col] != '.':
    #                 if game['mask'][row][col] == False:
    #                     revealed += dig_2d(game, row, col)
    #     if 0 <= row+1 < num_rows:
    #         if 0 <= col < num_cols:
    #             if game['board'][row+1][col] != '.':
    #                 if game['mask'][row+1][col] == False:
    #                     revealed += dig_2d(game, row+1, col)
    #     if 0 <= row-1 < num_rows:
    #         if 0 <= col+1 < num_cols:
    #             if game['board'][row-1][col+1] != '.':
    #                 if game['mask'][row-1][col+1] == False:
    #                     revealed += dig_2d(game, row-1, col+1)
    #     if 0 <= row < num_rows:
    #         if 0 <= col+1 < num_cols:
    #             if game['board'][row][col+1] != '.':
    #                 if game['mask'][row][col+1] == False:
    #                     revealed += dig_2d(game, row, col+1)
    #     if 0 <= row+1 < num_rows:
    #         if 0 <= col+1 < num_cols:
    #             if game['board'][row+1][col+1] != '.':
    #                 if game['mask'][row+1][col+1] == False:
    #                     revealed += dig_2d(game, row+1, col+1)

    # bombs = 0  # set number of bombs to 0
    # covered_squares = 0
    # for r in range(game['dimensions'][0]):
    #     # for each r,
    #     for c in range(game['dimensions'][1]):
    #         # for each c,
    #         if game['board'][r][c] == '.':
    #             if  game['mask'][r][c] == True:
    #                 # if the game mask is True, and the board is '.', add 1 to
    #                 # bombs
    #                 bombs += 1
    #         elif game['mask'][r][c] == False:
    #             covered_squares += 1
    # bad_squares = bombs + covered_squares
    # if bad_squares > 0:
    #     game['state'] = 'ongoing'
    #     return revealed
    # else:
    #     game['state'] = 'victory'
    #     return revealed


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
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    #if xray: return [[' ' if j == 0 else str(j) for j in i] for i in game['board']]
    return [['_' if not(t or xray) else ' ' if j == 0 else str(j) for j, t in zip(i, k)] for i, k in zip(game['board'], game['mask'])]


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
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    return '\n'.join([''.join(i) for i in render_2d(game, xray)])



# N-D IMPLEMENTATION
def valid_location(dim, location):
    """
    Returns all valid locations given board dimensions
    """
    return all(0<=location[i]<dim[i] for i in range(len(dim)))
        
def valid_locations(dim):
    """
    Returns all valid locations given board dimensions
    """
    if len(dim) == 1:
        return {(i,) for i in range(dim[0])}
    return {(i,) + j for j in valid_locations(dim[1:]) for i in range(dim[0])}
    
def valid_neighbors(dim, loc):
    '''a'''
    # point = list(loc)
    def neighbors_recursion(point):
        '''a'''
        neighbors = []
        # 1-dimension
        if len(point) == 1:
            neighbors.append([point[0] - 1])  # left
            neighbors.append([point[0]])  # current
            neighbors.append([point[0] + 1])  # right
            return neighbors

        # n-dimensional
        for sub_dimension in neighbors_recursion(point[1:]):
            neighbors.append([point[0] - 1] + sub_dimension)  # left
            neighbors.append([point[0]] + sub_dimension)  # center
            neighbors.append([point[0] + 1] + sub_dimension)  # right
        return neighbors
    res = set()
    for n in neighbors_recursion(list(loc)):
        if valid_location(dim, n): res.add(tuple(n))
    
    return res-{loc}

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

    def grid(dim, val):
        '''a'''
        if len(dim) == 1:
            return [val for i in range(dim[0])]
    
        return [grid(dim[1:], val) for i in range(dim[0])]
    
    board = grid(dimensions, 0)
    mask = grid(dimensions, False)
    
    for loc in bombs:
        str_loc = "["+"][".join([str(i) for i in loc])+"]"
        exec("board"+str_loc+"= '.'")
            
    bomb_set = set(bombs)
    for bomb_loc in bombs:
        for n in valid_neighbors(dimensions, bomb_loc):
            if n in bomb_set: continue
            str_loc = "["+"][".join([str(i) for i in n])+"]"
            exec("board"+str_loc+"+= 1")
        
    return {
        'dimensions': dimensions,
        'board' : board,
        'mask' : mask,
        'state': 'ongoing',}


def dig_nd(game, coordinates, visited = None, bomb_locations = None, non_bomb_loc = None):
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

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
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
    if visited is None:
        visited = set()

    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0 # keep the state the same

    if coordinates in visited:
        return 0
    visited.add(coordinates)
    str_coord = "["+"][".join([str(i) for i in coordinates])+"]"
    current = eval("game['mask']" +str_coord)
    if current == True: return 0
    exec("game['mask']"+str_coord+" = True")
    
    def bomb_set(board, dim):
        """
        Returns all valid locations given board dimensions
        """
        if len(dim) == 1:
            return {(i,) for i in range(dim[0]) if board[i]== '.'}
        x = set()
        for idx, k in enumerate(board):
            for j in bomb_set(k, dim[1:]):
                x.add((idx,)+j)
        return x
    
    if bomb_locations == None:
        bomb_locations = bomb_set(game['board'], game['dimensions'])
    
    if non_bomb_loc == None:
        non_bomb_loc = valid_locations(game['dimensions']) - bomb_locations
    #print(non_bomb_loc)
    for loc in non_bomb_loc:
        str_loc = "["+"][".join([str(i) for i in loc])+"]"
        lol = eval("game['mask']"+str_loc)
        if lol == False: break
        #print(t)
    else:
        game['state'] = 'victory'
        return 1
    lala = eval("game['board']"+str_coord)
    if lala == '.': game['state'] = 'defeat'
    if lala != 0: return 1

    
    count = 1
    for n in valid_neighbors(game['dimensions'], coordinates):
        if n not in bomb_locations:
            count += dig_nd(game, n, visited, bomb_locations, non_bomb_loc)
    return count


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
    
    def boards(board,mask, dim, xray):
        """
        hello there!
        """
        if len(dim) == 1:
            return ['_' if not xray and not k else ' ' if i == 0 else str(i) for i,k in zip(board, mask)]
        return [boards(l, m, dim[1:], xray) for l, m in zip(board, mask)]
    
    return boards(game['board'], game['mask'], game['dimensions'], xray)


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

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
    #doctest.run_docstring_examples(dig_2d, globals(), optionflags=_doctest_flags, verbose=False)
    # doctest.run_docstring_examples(render_nd, globals(), optionflags=_doctest_flags, verbose=False)
