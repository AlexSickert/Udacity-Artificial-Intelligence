assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'



def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values



def naked_twins(values):
    new_values = values.copy()
    naked_twins = []
    for box in new_values:
        if len(new_values[box]) == 2:
            for peer in peers[box]:
                if box < peer and new_values[peer] == new_values[box]:
                    naked_twins.append([box, peer])
    for nt in naked_twins:
        # Find the units that contains these two naked twins
        units = [u for u in unitlist if nt[0] in u and nt[1] in u]
        for unit in units:
            for box in unit:
                if box != nt[0] and box != nt[1]:
                    assign_value(new_values, box, new_values[box].replace(new_values[nt[0]][0], ''))
                    assign_value(new_values, box, new_values[box].replace(new_values[nt[0]][1], ''))
    if len([box for box in new_values.keys() if len(new_values[box]) == 0]):
        return False
    return new_values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

def diagonal(r, c):
    d_up = []
    d_down = []
    i_max = len(r) - 1 
        
    for i in range(9):
        i_inv = (i - i_max) * -1
        up = str(r[i_inv]) + str(c[i])
        down = str(r[i]) + str(c[i])
#        print("up: " + up)
#        print("down: " + down)
        d_up.append(up)
        d_down.append(down)
#        print(i)
        
#    print([d_up] + [d_up])
    return [d_up] + [d_down]
#    return [d_up] 
    

diagonal_units = diagonal(rows, cols)

print(diagonal_units)

row_units = [cross(r, cols) for r in rows]
#print(row_units)
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units + diagonal_units
#unitlist = row_units + column_units + square_units 
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
#print(units)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
#print(peers)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def grid_values_naked(grid):
   
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(".")
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
#    grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    values = grid_values(grid)
#values = reduce_puzzle(values)
    print(values)
    values = search(values)
    return values

if __name__ == '__main__':
    
    grid_str = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    
    solve(grid_str)
    
    
    
    