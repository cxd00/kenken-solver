from copy import deepcopy
count = 1  # counts iterations


def solve():
    board, rules, boardSize, pieces = readFile()
    solution = [[0 for z in range(boardSize)] for z in range(boardSize)]
    if backtrack1(board, (0, 0), pieces, solution, rules):
        return solution


def readFile():
    # initial formatting done here
    f = map(str.split, open("input.txt"))

    boardSize = int(f[0][0])
    board = []
    # creates the board of letters
    pieces = {}
    # adds pieces to a dictionary
    for k in range(0, boardSize):
        board.append(str(f[k + 1]).strip("['']"))
        for l in range(0, boardSize):

            if not board[k][l] in pieces:
                # check if piece has already been added to the dictionary
                p = Piece(board[k][l])
                # create a new piece
                p.coords[(k, l)] = 0
                pieces[board[k][l]] = p
                # adds the coordinate to the piece, val = letter
            else:
                # if piece is in the dictionary, just add to the coordinates
                pieces[board[k][l]].coords[(k, l)] = 0

    rules = {}
    # adds rules in the format key = letter, value = (number, operation)
    for line in f[boardSize + 1:]:
        line = line[0].strip("['']").split(':')
        rules[line[0]] = (line[1][:-1], line[1][-1:])
        if rules[line[0]][0] == '':
            rules[line[0]] = (rules[line[0]][1], '+')

    return board, rules, boardSize, pieces


def findRepeats(solution, coordinate, number):
    # finds repeats in the row or column
    if number in solution[coordinate[0]]:
        # check row
        return 1
    for m in range(0, len(solution[coordinate[0]])):
        # check column
        if int(solution[m][coordinate[1]]) == number:
            return 1
    return 0


def mathCheck(solution, rule, piece):
    # checks if the math for each piece works out, returns 0 if the math does not work
    # for one-cell pieces
    if len(piece.coords) == 1:
        if int(piece.coords.values()[0]) == int(rule[0]):
            piece.isSolved = 1
            return 1
        return 0
    operation = rule[1]

    big = piece.coords.values()[0]
    small = piece.coords.values()[1]
    if big < small:
        big = piece.coords.values()[1]
        small = piece.coords.values()[0]

    total = operationIterator(operation, big, small, piece, solution)
    piece.emptyCells = 0

    for value in piece.coords.values():
        if int(value) == 0:
            piece.emptyCells = piece.emptyCells + 1

    if not piece.isFilled:
        # cuts off the search when there's no way for the current values to get to the answer based on calculations
        empty = total
        if operation == '+':
            for x in range(0, piece.emptyCells):
                empty = empty + len(solution) - x
            if total > float(rule[0]) or empty < float(rule[0]):
                return 0
        if operation == '*':
            for x in range(0, piece.emptyCells):
                empty = empty * (len(solution) - x)
            if total > float(rule[0]) or empty < float(rule[0]):
                return 0
            for divisor in piece.coords.values():
                if not divisor == 0:
                    if not float(rule[0]) % divisor == 0:
                        return 0
        return 1

    if piece.isFilled and total == float(rule[0]):
        piece.isSolved = 1
        return 1
    return 0


def operationIterator(operation, big, small, piece, solution):
    # checks which operation and performs said operation
    total = 0
    if operation == '-':
        total = big - small

    elif operation == '/':
        if not small == 0:
            total = big / small

    elif operation == '+':
        for coordinate in piece.coords:
            total += solution[coordinate[0]][coordinate[1]]

    elif operation == '*':
        total = 1
        for coordinate in piece.coords:
            if not solution[coordinate[0]][coordinate[1]] == 0:
                total = total * solution[coordinate[0]][coordinate[1]]

    return total


def findRemainingValues(solution, coordinate, valuesToTry):
    # finds the values still available for use (no repeats)
    copyValuesToTry = valuesToTry[:]
    for num in range(1, len(solution) + 1):
        if findRepeats(solution, coordinate, num):
            copyValuesToTry.remove(num)
    return copyValuesToTry


def findMRV(board, coordinate, solution, values):
    # returns the post-constraints-filter values, most constrained first. This prunes the tree.
    i = coordinate[0]
    j = coordinate[1]
    mrv = {}
    soln = deepcopy(solution)

    for num in values:
        if j == len(board) - 1:
            i = i + 1
            j = 0
        else:
            j = j + 1
        if i == len(board) or j == len(board):
            mrv[num] = 1
        else:
            mrv[num] = len(findRemainingValues(soln, (i, j), range(1, len(board) + 1)))
    return sorted(mrv.items(), key=lambda x: x[1])


def counter():
    # just for returning the number of iterations
    global count
    count = count + 1
    if count > 10000000:
        "Program has recursed through 10 million nodes. Would advise stopping the program."


def backtrack1(board, coordinate, pieces, solution, rules):
    # this is the main backtracking (improved) function. Finds all possible values, given the constraints, and
    # returns them in order of most to least constrained. Recurses until the grid is full, correctly.

    counter()
    i = coordinate[0]
    j = coordinate[1]

    if all(value.isSolved == 1 for value in pieces.values()):
        return 1
    elif i == len(board) or j == len(board):
        return 0

    piece = pieces[board[i][j]]
    piece.isFilled = 1
    rule = rules[board[i][j]]

    valuesToTry = findRemainingValues(solution, coordinate, range(1, len(board) + 1))
    if not valuesToTry:
        solution[i][j] = 0
        piece.coords[coordinate] = 0
        return 0

    mrv = findMRV(board, coordinate, solution, valuesToTry)
    for num in mrv:
        num = num[0]
        solution[i][j] = num
        for cell in range(j + 1, len(board)):
            solution[i][cell] = 0
        piece.coords[coordinate] = num

        for val in piece.coords.keys():
            if piece.coords[val] == 0:
                piece.isFilled = 0
        mathPass = mathCheck(solution, rule, piece)
        if len(valuesToTry) < 2 and not mathPass:
            solution[i][j] = 0
            piece.coords[coordinate] = 0
            return 0
        if num in valuesToTry:
            valuesToTry.remove(num)

        if mathPass:
            if j == len(board) - 1:
                if backtrack1(board, (i + 1, 0), pieces, solution, rules):
                    return 1
            else:
                if backtrack1(board, (i, j + 1), pieces, solution, rules):
                    return 1
    solution[i][j] = 0
    piece.coords[coordinate] = 0
    return 0


class Piece:
    # this class creates each piece

    def __init__(self, letter):
        self.isSolved = 0
        self.isFilled = 0
        self.letter = letter
        self.coords = {}
        self.emptyCells = len(self.coords)


# printing...
sol = solve()

row = ''
for a in range(0, len(sol)):
    for b in range(0, len(sol)):
        row = row + ' ' + str(sol[a][b])
    print row
    row = ''
print "Improved Backtracking: Generated with {} recursive calls.".format(count)


