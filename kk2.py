import numpy as np


def solve():
    board, rules, boardSize, pieces = readFile()
    arr = np.arange(1, boardSize + 1)
    print arr
    solution = [0]*boardSize
    for i in range(0, boardSize):
        np.random.shuffle(arr)
        solution[i] = np.copy(arr)
    print solution
    # if localSearch(board, (0, 0), pieces, solution, rules):
    #     return solution


def readFile():
    f = map(str.split, open("input2.txt"))

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

    return board, rules, boardSize, pieces


def localSearch(board, coordinates, pieces, solution, rules):
    # do nothing
    i = 1


class Piece:

    def __init__(self, letter):
        self.isSolved = 0
        self.isFilled = 0
        self.letter = letter
        self.coords = {}
        self.emptyCells = len(self.coords)


solve()