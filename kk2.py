import collections
import sys
import numpy as np


def solve():
    board, rules, boardSize, pieces, solution = readFile()
    minCost = makeConflictBoard(solution, pieces, rules)
    currSolution = np.copy(solution)
    minSolution = np.copy(currSolution)
    print solution
    temperature = 1
    for loop in range(50):
        currSolution, currCost = localSearch(board, pieces, minSolution, rules, 50, temperature)
        if currCost == 0:
            return currSolution, 0
        if currCost < minCost:
            minSolution = currSolution
            minCost = currCost
        np.random.shuffle(currSolution)
        temperature = temperature - 0.005
    return minSolution, minCost


def findRemainingValues(solution, coordinate, valuesToTry):
    # finds the values still available for use (no repeats)
    copyValuesToTry = valuesToTry[:]
    for num in range(1, len(solution) + 1):
        if findRepeats0(solution, coordinate, num):
            copyValuesToTry.remove(num)
    return copyValuesToTry


def findRepeats0(solution, coordinate, number):
    # finds repeats in the row or column
    if number in solution[coordinate[0]]:
        # check row
        return 1
    for m in range(0, len(solution[coordinate[0]])):
        # check column
        if int(solution[m][coordinate[1]]) == number:
            return 1
    return 0


def backtrack0(coordinate, solution):
    i = coordinate[0]
    j = coordinate[1]

    if i == len(solution) or j == len(solution):
        return 1

    valuesToTry = findRemainingValues(solution, coordinate, range(1, len(solution) + 1))
    np.random.shuffle(valuesToTry)
    if not valuesToTry:
        return 0

    for num in valuesToTry:
        solution[i][j] = num

        if num in valuesToTry:
            valuesToTry.remove(num)

        if j == len(solution) - 1:
            if backtrack0((i + 1, 0), solution):
                return 1
        else:
            if backtrack0((i, j + 1), solution):
                return 1

    solution[i][j] = 0
    return 0


def readFile():
    f = map(str.split, open("input.txt"))

    boardSize = int(f[0][0])
    board = []
    # creates the board of letters
    pieces = {}
    # adds pieces to a dictionary
    arr = np.arange(1, boardSize+1)
    solution = [0]*boardSize
    #backtrack0((0, 0), solution)

    for k in range(0, boardSize):
        board.append(str(f[k + 1]).strip("['']"))
        np.random.shuffle(arr)
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

    return board, rules, boardSize, pieces, solution


def findViolations(solution, rules, pieces, board):
    violations = {}
    for i in range(len(solution)):
        for j in range(len(solution)):
            letter = board[i][j]
            if findRepeats0(solution, (i, j), solution[i][j]) or not mathCheck(solution, rules[letter], pieces[letter]):
                violations[(i, j)] = solution[i][j]
    return violations


def localSearch(board, pieces, solution, rules, maxSteps, temperature):
    violations = findViolations(solution, rules, pieces, board)
    tempSolution = np.copy(solution)
    minSolution = np.copy(tempSolution)
    for i in range(maxSteps):
        if not violations:
            return i, minSolution
        for violationCoord in violations.keys():
            i, j = violationCoord[0], violationCoord[1]
            minCost = makeConflictBoard(minSolution, pieces, rules)
            # cost = makeConflictBoard(minSolution, pieces, rules)
            for num in range(0, len(board)):
                # swap through row
                rowSolution = np.copy(tempSolution)
                t = rowSolution[i][j]
                rowSolution[i][j] = rowSolution[i][num]
                rowSolution[violationCoord[0]][num] = t
                rowCost = makeConflictBoard(rowSolution, pieces, rules)
                # rowCost = len(findViolations(rowSolution, rules, pieces, board))

                # swap through column
                colSolution = np.copy(tempSolution)
                t = colSolution[i][j]
                colSolution[i][j] = colSolution[num][j]
                colSolution[num][j] = t
                colCost = makeConflictBoard(colSolution, pieces, rules)
                # colCost = len(findViolations(colSolution, rules, pieces, board))

                if rowCost <= colCost:
                    cost = rowCost
                    tempSolution = rowSolution
                else:
                    cost = colCost
                    tempSolution = colSolution

                if cost == 0:
                    return tempSolution, cost

                if cost <= minCost or np.exp(-(minCost-cost)/temperature) > np.random.random_sample():
                    minCost = cost
                    minSolution = tempSolution
            violations = findViolations(tempSolution, rules, pieces, board)
    return minSolution, minCost

    # current = np.copy(solution)
    # minCost = makeConflictBoard(current, pieces, rules)
    #
    # for i in range(maxSteps):
    #     if minCost == 0:
    #         return current
    #     potentialSwap = findSwap(current, np.random.randint(1, len(current), size=2), pieces, rules, board)
    #     # potentialSwap = findSwap(current, (0, 0), pieces, rules)
    #     cost = makeConflictBoard(potentialSwap, pieces, rules)
    #     if minCost > cost:
    #         current = potentialSwap
    #         minCost = cost
    #
    # return current, minCost


def findSwap(solution, coordinate, pieces, rules, board):
    current = np.copy(solution)
    minCost = makeConflictBoard(current, pieces, rules)
    minBoard = current
    letter = board[coordinate[0]][coordinate[1]]
    # letter of the original piece being swapped
    for i in range(len(current)):
        tempLetter = board[coordinate[0]][i]
        # letter of the other piece being swapped
        if pieces[letter].isSolved:
            if letter == tempLetter:
                original = np.copy(current)
                t = current[coordinate[0]][coordinate[1]]
                current[coordinate[0]][coordinate[1]] = np.copy(current[coordinate[0]][i])
                current[coordinate[0]][i] = t
                cost = makeConflictBoard(current, pieces, rules)
                if cost > minCost:
                    current = original
                else:
                    minCost = cost
                    minBoard = current
        else:
            if not letter == tempLetter:
                original = np.copy(current)
                t = current[coordinate[0]][coordinate[1]]
                current[coordinate[0]][coordinate[1]] = np.copy(current[coordinate[0]][i])
                current[coordinate[0]][i] = t
                cost = makeConflictBoard(current, pieces, rules)
                # cost = len(findViolations(solution, rules, pieces, board))
                if cost > minCost:
                    current = original
                else:
                    minCost = cost
                    minBoard = current

    return minBoard


def makeConflictBoard(solution, pieces, rules):
    totalConflicts = 0
    totalConflicts += findRepeats(solution)
    for letter in pieces.keys():
        totalConflicts += mathCheck(solution, rules[letter], pieces[letter])
    return totalConflicts


def findBestVal(solution, coordinate):
    conflicts = {}
    for current in range(1, len(solution) + 1):
        conflicts[current] = 0
        for i in range(0, len(solution)):
            if solution[coordinate[0]][i] == current:
                conflicts[current] += 1
            if solution[i][coordinate[1]] == current:
                conflicts[current] += 1
    return min(conflicts, key=conflicts.get)


# def findBestSwap(board, iterations, solution, coordinate, pieces, rules, tabu):
#     sol = np.copy(solution)
#     i = coordinate[0]
#     j = coordinate[1]
#     minConflicts = sys.maxint
#     for it in range(len(sol)):
#         if not (i, j) in tabu.itervalues() or not (i, it) in tabu.itervalues():
#             t = sol[i][j]
#             sol[i][j] = np.copy(sol[i][it])
#             pieces[board[i][j]].coords[(i, j)] = sol[i][j]
#             sol[i][it] = t
#             pieces[board[i][it]].coords[(i, it)] = t
#
#             tempConfl, temp = makeConflictBoard(sol, pieces, rules, board)
#             if temp < minConflicts:
#                 tabu[2 * (i % 6)] = (i, j)
#                 tabu[2 * (i % 6) + 1] = (i, it)
#                 minConflicts = temp
#     return sol, minConflicts

def findBestSwap(board, solution, coordinate, pieces, rules, temperature, iterations):
    sol = np.copy(solution)
    i = coordinate[0]
    j = coordinate[1]
    minConflicts = sys.maxint
    minConflictsBoard = {}
    for it in range(len(sol)):
        # t = sol[i][j]
        # sol[i][j] = np.copy(sol[it[0]][it[1]])
        # pieces[board[i][j]].coords[(i, j)] = sol[i][j]
        # sol[it[0]][it[1]] = t
        # pieces[board[it[0]][it[1]]].coords[it] = t
        t = sol[i][j]
        sol[i][j] = np.copy(sol[i][it])
        pieces[board[i][j]].coords[(i, j)] = sol[i][j]
        sol[i][it] = t
        pieces[board[i][it]].coords[(i, it)] = t

        tempConfl, temp = makeConflictBoard(sol, pieces, rules, board)
        diff = int(temp - minConflicts)
        annealingCoeff = np.exp(-(diff/temperature))
        if diff <= 0 or np.random.random < annealingCoeff:
            minConflicts = temp
            minConflictsBoard = tempConfl
        if iterations % 500 == 0 and temperature > 0.20:
            temperature -= 0.05
    return sol, minConflicts


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


def mathCheck(solution, rule, piece):
    # checks if the math for each piece works out

    # for one-cell pieces
    if len(piece.coords) == 1:
        total = int(piece.coords.values()[0])
        if total == int(rule[0]):
            piece.isSolved = 1
            return 0
        # return np.abs(10*(total - float(rule[0]))/(float(rule[0])*len(piece.coords)))
        return np.abs(total - int(rule[0]))

    operation = rule[1]
    big = piece.coords.values()[0]
    small = piece.coords.values()[1]
    total = operationIterator(operation, big, small, piece, solution)

    if total == float(rule[0]):
        piece.isSolved = 1
        return 0
    else:
        piece.isSolved = 0
        # return np.abs(10*(total - float(rule[0]))/(float(rule[0])*len(piece.coords)))
        return np.abs(total - int(rule[0]))


def operationIterator(operation, big, small, piece, solution):
    # checks which operation and performs said operation
    total = 0
    if operation == '-':
        if big < small:
            big = piece.coords.values()[1]
            small = piece.coords.values()[0]
        total = big - small

    elif operation == '/':
        if big < small:
            big = piece.coords.values()[1]
            small = piece.coords.values()[0]
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


class Piece:

    def __init__(self, letter):
        self.isSolved = 0
        self.isFilled = 1
        self.letter = letter
        self.coords = {}
        self.cells = len(self.coords)


sol = solve()
print sol