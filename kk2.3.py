import collections

import numpy as np


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
        solution.grid[k] = arr
        solution[k] = np.copy(arr)
        for l in range(0, boardSize):

            if not board[k][l] in pieces:
                # check if piece has already been added to the dictionary
                p = Piece(board[k][l])
                # create a new piece
                p.coords[(k, l)] = solution[k][l]
                pieces[board[k][l]] = p
                # adds the coordinate to the piece, val = letter
            else:
                # if piece is in the dictionary, just add to the coordinates
                pieces[board[k][l]].coords[(k, l)] = solution[k][l]

    rules = {}
    # adds rules in the format key = letter, value = (number, operation)
    for line in f[boardSize + 1:]:
        line = line[0].strip("['']").split(':')
        rules[line[0]] = (line[1][:-1], line[1][-1:])
        if rules[line[0]][0] == '':
            rules[line[0]] = (rules[line[0]][1], '+')

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
        violations.append(piece)
    return total


def mathCheck(solution, rule, piece):
    grid = solution.grid
    # checks if the math for each piece works out
    # for one-cell pieces
    if len(piece.coords) == 1:
        if int(piece.coords.values()[0]) == int(rule[0]):
            piece.isSolved = 1
            return piece.coords.values()[0]
        return 0
    operation = rule[1]

    big = piece.coords.values()[0]
    small = piece.coords.values()[1]
    if big < small:
        big = piece.coords.values()[1]
        small = piece.coords.values()[0]

    total = operationIterator(operation, big, small, piece, grid)
    piece.emptyCells = 0

    for value in piece.coords.values():
        if int(value) == 0:
            piece.emptyCells = piece.emptyCells + 1

    if not piece.isFilled:
        # cuts off the search when there's no way for the current values to get to the answer
        empty = total
        if operation == '+':
            for x in range(0, piece.emptyCells):
                empty = empty + len(grid) - x
            if total > float(rule[0]) or empty < float(rule[0]):
                return 0
        if operation == '*':
            for x in range(0, piece.emptyCells):
                empty = empty * (len(grid) - x)
            if total > float(rule[0]) or empty < float(rule[0]):
                return 0
            for divisor in piece.coords.values():
                if not divisor == 0:
                    if not float(rule[0]) % divisor == 0:
                        return 0
        return total


def findViolations(board, rules, solution):
    grid = solution.grid
    transposedGrid = np.array(grid).T
    violations = []

    # checks pieces for total, if total is wrong, add to violations
    for key in solution.pieces.keys():
        solution.pieces[key].total = checkPiece(solution, solution.pieces[key], rules, violations)

    # add rows or columns with repeats to violations
    for r in range(len(board)):
        rowCount = collections.Counter(grid[r])
        for key in rowCount:
            if rowCount[key] > 1:
                violations.append(grid[r])
        colCount = collections.Counter(transposedGrid[r])
        for key in colCount:
            if colCount[key] > 1:
                violations.append(transposedGrid[r])
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


def backtrackFill(violation, solution, rules):
    if isinstance(violation, Piece):
        rule = rules[violation.letter]
        for coordinate in violation.coords.keys():
            possibleValues = findPossibleValues(rule, range(1, len(solution.grid)))
            total = mathCheck(solution, rule, violation)



def localSearch(violations, solution, rules):
    for iteration in range(500):
        violation = collections.deque(violations).pop()
        backtrackFill(violation, solution, rules)


def solve():
    board, rules, boardSize, pieces, solution = readFile()



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
