def dump(game):
    """
    Print a normalized version of the game to the terminal
    """
    for key in ('board', 'dimensions', 'mask', 'state'):
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which can be
                     either tuples or lists

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
    Recursively dig up (row, col) and neighboring squares.

    Update game['mask'] to reveal (row, col); then recursively reveal (dig up)
    its neighbors, as long as (row, col) does not contain and is not adjacent
    to a bomb.  Return an integer indicating how many new squares were
    revealed.

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

    >>> game = {'dimensions': [2, 4],
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
    dimensions: [2, 4]
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
    return render_nd(game, xray=xray)


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
    return "\n".join("".join(r) for r in render_2d(game, xray=xray))



def make_nd_board(dims, fill):
    """
    Recursively construct an n-dimensional board filled with a given element.

    Arguments:
        dims: the dimensions of the board to be created
        fill: the element to put in the board
    >>> make_nd_board((1,2), 7)
    [[7, 7]]
    """
    if len(dims) == 1:
        return [fill] * dims[0]
    else:
        return [make_nd_board(dims[1:], fill) for i in range(dims[0])]


def nd_neighbors(loc, dims):
    """
    Generator to yield the neighbors of a given location.
    Note: also yields the given location

    Arguments:
        loc: the location whose neighbors we want to find
        dims: the dimensions of the space
    >>> dims = (1, 2, 3)
    >>> near = nd_neighbors((0, 1, 2), dims)
    >>> set(near) == {(0, 0, 1), (0, 1, 1), (0, 0, 2), (0, 1, 2)}
    True
    """
    if len(loc) == 0:
        # base case is 0-d
        # yield a single tuple so the 1-d case can build on this
        yield tuple()
    else:
        # recursive case.  find the neighbors of loc[1:] in a space of lower
        # dimensionality.  then add x-1, x, and x+1 to the front of each
        # neighbor in the lower-d space, where x is the coordinate in this
        # dimension.
        for j in nd_neighbors(loc[1:], dims[1:]):
            yield from (((x, )+j) for x in (loc[0]-1, loc[0], loc[0]+1) if 0<=x<dims[0])


def nd_get(array, loc):
    """
    Returns the element at the given location in the given array.
    >>> b = make_nd_board((1,2), 7)
    >>> nd_get(b, (0,1))
    7
    """
    if len(loc) == 1:
        return array[loc[0]]
    else:
        return nd_get(array[loc[0]], loc[1:])


def nd_set(array, loc, val):
    """
    Sets the element at the given location in the given array to be the given
    value.
    >>> b = make_nd_board((1,2), 7)
    >>> nd_set(b, (0,1), 77)
    >>> nd_get(b, (0,1))
    77
    >>> nd_get(b, (0,0))
    7
    """
    if len(loc) == 1:
        array[loc[0]] = val
    else:
        nd_set(array[loc[0]], loc[1:], val)


def all_coords(dims):
    """
    Generator to yield all the coordinates in a space with the given
    dimensionality.
    >>> set(all_coords((3,))) == {(0,), (1,), (2,)}
    True
    >>> set(all_coords((1,2))) == {(0,1), (0,0)}
    True
    """
    if len(dims) == 0:
        yield tuple()
    else:
        yield from ((i, )+j for j in all_coords(dims[1:]) for i in range(dims[0]))

def is_victory(game):
    """
    Return True if the given game represents a victory condition, and False
    otherwise.
    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> is_victory(g)
    False
    """
    for c in all_coords(game['dimensions']):
        brd = nd_get(game['board'], c)
        msk = nd_get(game['mask'], c)
        # two things mean we have not won:
        if brd == '.' and msk:  # a bomb that has been uncovered.
            return False
        if brd != '.' and not msk:  # a safe square that has not be uncovered.
            return False
    return True


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensionss (list): Dimensions of the board
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
    out = {
        'board': make_nd_board(dimensions, 0),
        'mask': make_nd_board(dimensions, False),
        'dimensions': dimensions,
        'state': 'ongoing',
    }
    for b in bombs:
        nd_set(out['board'], b, '.')
        for n in nd_neighbors(b, dimensions):
            v = nd_get(out['board'], n)
            if isinstance(v, int):
                nd_set(out['board'], n, v+1)
    return out


def dig_nd(game, coords, check_victory=True):
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
       coords (list): Where to start digging

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
    if game['state'] != 'ongoing' or nd_get(game['mask'], coords):
        return 0

    nd_set(game['mask'], coords, True)

    this_spot = nd_get(game['board'], coords)
    if this_spot == '.':
        game['state'] = 'defeat'
        return 1

    count = 1
    if this_spot == 0:
        for n in nd_neighbors(coords, game['dimensions']):
            count += dig_nd(game, n, check_victory=False)

    if check_victory and is_victory(game):
        game['state'] = 'victory'
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
    out = make_nd_board(game['dimensions'], None)
    for c in all_coords(game['dimensions']):
        brd = nd_get(game['board'], c)
        msk = nd_get(game['mask'], c)
        nd_set(out, c, '_' if not xray and not msk else ' ' if brd == 0 else str(brd))
    return out


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
