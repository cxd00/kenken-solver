import collections
import copy
import numpy as np


# This local search algorithm first reads in all of the information from the input file, generating a random solution board.
# Next, it generates a list of violated pieces, rows, and columns.
# Violations are popped off of this list, and depending on whether the violation is a row, column, or piece, a swap is conducted
# The best node is saved, with a staleness factor that shuffles the best node once it's been repeated 50 times.


def readFile():
    f = map(str.split, open("input.txt"))

    boardSize = int(f[0][0])
    board = []
    # creates the board of letters
    pieces = {}
    # adds pieces to a dictionary
    arr = np.arange(1, boardSize+1)
    solution = Solution(boardSize)

    for k in range(0, boardSize):
        board.append(str(f[k + 1]).strip("['']"))
        np.random.shuffle(arr)
        solution.grid[k] = np.copy(arr)
        for l in range(0, boardSize):

            if not board[k][l] in pieces:
                # check if piece has already been added to the dictionary
                p = Piece(board[k][l])
                # create a new piece
                p.coords[(k, l)] = solution.grid[k][l]
                pieces[board[k][l]] = p
                # adds the coordinate to the piece, val = letter
            else:
                # if piece is in the dictionary, just add to the coordinates
                pieces[board[k][l]].coords[(k, l)] = solution.grid[k][l]

    rules = {}
    # adds rules in the format key = letter, value = (number, operation)
    for line in f[boardSize + 1:]:
        line = line[0].strip("['']").split(':')
        rules[line[0]] = (line[1][:-1], line[1][-1:])
        if rules[line[0]][0] == '':
            rules[line[0]] = (rules[line[0]][1], '+')

    solution.pieces = pieces
    updatePieces(board, solution)
    return board, rules, boardSize, pieces, solution


def updatePieces(board, solution):
    for x in range(len(board)):
        for y in range(len(board)):
            solution.pieces[board[x][y]].coords[(x, y)] = int(solution.grid[x][y])


def operationIterator(operation, big, small, piece, grid):
    # checks which operation and performs said operation
    total = 0
    if operation == '-':
        total = big - small

    elif operation == '/':
        if not small == 0:
            total = big / small

    elif operation == '+':
        for coordinate in piece.coords:
            total += grid[coordinate[0]][coordinate[1]]

    elif operation == '*':
        total = 1
        for coordinate in piece.coords:
            if not grid[coordinate[0]][coordinate[1]] == 0:
                total = total * grid[coordinate[0]][coordinate[1]]

    return total


def checkPiece(solution, piece, rules, violations):
    # checks if the piece maths up to the right value
    rule = rules[piece.letter]
    total = mathCheck(solution, rule, piece)
    if total == 0:
        violations.append(("piece", piece))
    return total


def mathCheck(solution, rule, piece):
    grid = solution.grid
    # checks if the math for each piece works out
    # for one-cell pieces
    if len(piece.coords) == 1:
        if int(piece.coords.values()[0]) == int(rule[0]):
            piece.isSolved = 1
            return piece.coords.values()[0]
        return abs(int(rule[0]) - piece.coords.values()[0])
    operation = rule[1]

    big = piece.coords.values()[0]
    small = piece.coords.values()[1]
    if big < small:
        big = piece.coords.values()[1]
        small = piece.coords.values()[0]

    total = operationIterator(operation, big, small, piece, grid)
    return abs(float(rule[0]) - total)

    piece.emptyCells = 0

    for value in piece.coords.values():
        if int(value) == 0:
            piece.emptyCells = piece.emptyCells + 1
        return total


def findViolations(board, rules, solution):
    grid = solution.grid
    transposedGrid = np.array(grid).T
    violations = []

    # checks pieces for total, if total is wrong, add to violations
    for key in solution.pieces.keys():
        solution.pieces[key].total = checkPiece(solution, solution.pieces[key], rules, violations)
        if not solution.pieces[key].total == rules[solution.pieces[key].letter][0]:
            violations.append(("piece", solution.pieces[key]))

    # add rows or columns with repeats to violations
    for r in range(len(board)):
        rowCount = collections.Counter(grid[r])
        for key in rowCount:
            if rowCount[key] > 1:
                violations.append(("row", grid[r], r))
        colCount = collections.Counter(transposedGrid[r])
        for key in colCount:
            if colCount[key] > 1:
                violations.append(("col", transposedGrid[r], r))
    return violations


def checkForRepeats(grid, coordinate, number):
    # finds repeats in the row or column
    if number in grid[coordinate[0]]:
        # check row
        return 1
    for m in range(0, len(grid[coordinate[0]])):
        # check column
        if int(grid[m][coordinate[1]]) == number:
            return 1
    return 0


def findPossibleValues(rule, valuesToTry):
    possibleValues = valuesToTry
    for val in possibleValues:
        if rule[1] == '*':
            if not int(rule[0]) % val == 0:
                possibleValues.remove(val)
        if rule[1] == '+':
            if not val < int(rule[0]):
                possibleValues.remove(val)
    return possibleValues


def findRepeatsSpecific(grid, coordinate, number):
    total = -2
    # finds repeats in the row or column
    for i in range(len(grid)):
        # check row
        if grid[coordinate[0]][i] == number and not i == coordinate[1]:
            total += 1
            return 1
        if grid[i][coordinate[1]] == number and not i == coordinate[0]:
            total += 1
            return 1
    return 0


def findRepeats(solution):
    total = 0
    # finds repeats in the row or column
    for i in range(len(solution)):
        # check row
        rowCount = collections.Counter(solution[i])
        col = [row[i] for row in solution]
        colCount = collections.Counter(col)
        for j in range(1, len(solution)+1):
            if rowCount[j] > 1:
                total += rowCount[j] - 1
            if colCount[j] > 1:
                total += colCount[j] - 1
    return total


def findRemainingValues(solution, coordinate, valuesToTry):
    grid = solution.grid
    # finds the values still available for use (no repeats)
    copyValuesToTry = valuesToTry[:]
    for num in range(1, len(grid) + 1):
        if findRepeatsSpecific(grid, coordinate, num) > 0:
            copyValuesToTry.remove(num)
    return copyValuesToTry


def updateConflicts(solution, pieces, rules):
    grid = solution.grid
    totalConflicts = 0
    totalConflicts += findRepeats(grid)
    for letter in pieces.keys():
        totalConflicts += mathCheck(solution, rules[letter], pieces[letter])
    solution.fitness = totalConflicts
    return totalConflicts


def swap(type, violation, solution, rules, board):
    swapToIndex = np.random.randint(len(solution.grid))
    if type == "row":
        while swapToIndex == violation[2]:
            swapToIndex = np.random.randint(len(solution.grid))
        temprow = np.copy(solution.grid[violation[2]])
        solution.grid[violation[2]] = solution.grid[swapToIndex]
        solution.grid[swapToIndex] = temprow

    else:
        for i in range(len(solution.grid)):
            tempcol = np.copy(solution.grid[i][violation[2]])
            solution.grid[i][violation[2]] = solution.grid[i][swapToIndex]
            solution.grid[i][swapToIndex] = tempcol

    updatePieces(board, solution)
    updateConflicts(solution, solution.pieces, rules)


def localSearch(violations, solution, rules, board):
    staleness = 0
    best = copy.deepcopy(solution)
    minConstraints = best.fitness
    iterations = 0
    while len(violations) > 0 and iterations < 10000:

        if best.fitness < 1.0:
            return best, best.fitness, iterations

        current = copy.deepcopy(best)

        if staleness > 50:
            current = copy.deepcopy(best)
            np.random.shuffle(best.grid)
            # print "shuffled"

        np.random.shuffle(violations)
        violation = collections.deque(violations).pop()
        # violation is a three-tuple for rows/cols (type, row/col, index)
        # for pieces, it's a tuple (type, piece)
        if violation[0] == "row" or violation[0] == "col":
            swap(violation[0], violation, current, rules, board)

        else:
            piece = copy.deepcopy(violation[1])
            coordinates = piece.coords.keys()
            np.random.shuffle(coordinates)
            if not len(piece.coords) < 2:
                val = piece.coords[coordinates[0]]
                randIndex = np.random.randint(len(current.grid))
                current.grid[coordinates[0][0]][coordinates[0][1]] = current.grid[coordinates[0][0]][randIndex]
                current.grid[coordinates[0][0]][randIndex] = val
                current.piece = piece
            updatePieces(board, current)
            updateConflicts(current, current.pieces, rules)

        if minConstraints > current.fitness:
            best = copy.deepcopy(current)
            minConstraints = best.fitness
        if minConstraints == current.fitness:
            staleness += 1
        violations = findViolations(board, rules, best)
        iterations += 1

    return best, best.fitness, iterations

def solve():
    board, rules, boardSize, pieces, solution = readFile()
    violations = findViolations(board, rules, solution)
    updateConflicts(solution, pieces, rules)
    return localSearch(violations, solution, rules, board)



class Piece:

    def __init__(self, letter):
        self.isSolved = 0
        self.isFilled = 1
        self.letter = letter
        self.coords = {}
        self.cells = len(self.coords)
        self.total = 0


class Solution:

    def __init__(self, boardSize):
        self.fitness = 0
        self.grid = np.zeros((boardSize, boardSize), dtype=int)
        self.pieces = {}


x, fitness, y = solve()

row = ''
for a in range(0, len(x.grid)):
    for b in range(0, len(x.grid)):
        row = row + ' ' + str(x.grid[a][b])
    print row
    row = ''
msg = "No solution was found, this was the best solution generated in {} iterations."
if not fitness == 0:
    print msg.format(y)
else:
    print "Solution found in {} iterations".format(y)
