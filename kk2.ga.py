import collections
import copy
import sys
import numpy as np

# This is my attempt at the genetic algorithm. I would not advise running this with a 6x6 puzzle or greater, as
# it will more likely than not spit out a board that is far from correct.


def solve():
    board, rules, boardSize, pieces = readFile()
    population = generatePopulation([], board, rules, pieces)
    x, y = geneticSearch(population, board, rules, pieces)
    return x, x.fitness, y


def checkForRepeats(solution):
    # takes in a solution object, returns a 1 if there are repeats anywhere in a row or column
    grid = solution.grid
    transposedGrid = copy.deepcopy(grid).T
    for i in range(len(grid)):
        rowCount = collections.Counter(grid[i])
        colCount = collections.Counter(transposedGrid[i])

        if len(rowCount) < len(grid) or len(colCount) < len(grid):
            return 1  # there are repeats
    return 0


def geneticSearch(population, board, rules, pieces):
    # genetic algorithm attempt:
    # takes a population and "reproduces" over randomly generated members of the population
    # mutates when the best 3 values become stale
    # adjustingSwap called to make a swap 40% of the time

    iterations = 0
    length = len(population)
    globalBest = population[length-1]
    localMaximumFitness = 0

    while iterations < length:
        # finds the best "chromosome", or solution
        if globalBest.fitness < population[length-1].fitness:
            globalBest = population[length-1]

        for chromosome in range(length):
            fitness = population[chromosome].fitness
            if fitness == 1:
                return population[chromosome], iterations

        newPopulation = []

        population.sort(key=fitnessSort)
        best = []
        for m in range(1, 4):
            # copies out the best 3 to keep them from getting lost in the reproduction
            best.append(copy.deepcopy(population[length-m]))
        if best[1].grid.all() == best[2].grid.all():
            localMaximumFitness += 1  # checks for staleness in the 3 best
        if localMaximumFitness > 3:
            best[1] = mutate(best[1], board, rules)
            best[2] = mutate(best[2], board, rules)

        while len(newPopulation) <= length-3:
            # for the rest, "chromosomes" or solutions are mated
            p = findProbabilities(population)
            choices = np.random.choice(population, 2, p)
            solution1, solution2 = reproduce(choices[0], choices[1], board, rules)

            if solution1.fitness == 1:
                return solution1
            elif solution2.fitness == 1:
                return solution2
            if solution1.fitness < solution2.fitness or np.random.rand > 0.90:
                fittestChild = solution1
            else:
                fittestChild = solution2

            if np.random.rand() < 0.4 and not checkForRepeats(fittestChild):
                # 40% of the time, the child, if lacking repeats, is swapped around a bit.
                fittestChild = adjustingSwap(fittestChild, board, rules)
                fittestChild.fitness = getFitness(fittestChild, board)

            newPopulation.append(fittestChild)

        for b in best:
            newPopulation.append(b)

        newPopulation.sort(key=fitnessSort)
        population = newPopulation
        iterations += 1

    return globalBest, iterations


def mutate(solution, board, rules):
    # unless the solution is very close to being perfect, mutation by swapping values in a row
    if solution.fitness < 0.96:
        row = np.arange(1, len(solution.grid))
        vals = np.random.choice(row, 3)

        temp = solution.grid[vals[0]][vals[1]]
        solution.grid[vals[0]][vals[1]] = solution.grid[vals[0]][vals[2]]
        solution.grid[vals[0]][vals[2]] = temp

        updatePieces(board, solution, rules)
    return solution


def findProbabilities(population):
    # calculates the probability of being picked to reproduce => favors the "fitter" parents, but only slightly
    # given the large number of "chrosomes" and the relatively small differences in fitness
    totalFitness = 0
    probability = []
    for i in range(len(population)):
        totalFitness += population[i].fitness

    for i in range(len(population)):
        population[i].probability = population[i].fitness / totalFitness
        probability.append(population[i].probability)

    return probability


def reproduce(solution1, solution2, board, rules):
    # reproduces by swapping two rows between the two parents
    x, y = np.random.randint(1, len(solution1.grid)), np.random.randint(1, len(solution1.grid))

    temp1x = solution1.grid[x]
    temp1y = solution1.grid[y]
    temp2x = solution2.grid[x]
    temp2y = solution2.grid[y]

    sol1 = copy.deepcopy(solution1)
    sol2 = copy.deepcopy(solution2)

    sol1.grid[y] = temp2x
    sol1.grid[x] = temp2y
    sol2.grid[y] = temp1x
    sol2.grid[x] = temp1y

    sol1.fitness = getFitness(sol1, board)
    sol2.fitness = getFitness(sol2, board)

    updatePieces(board, sol1, rules)
    updatePieces(board, sol2, rules)

    return sol1, sol2


def fitnessSort(elem):
    # function just for
    return elem.fitness


def readFile():
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
            rules[line[0]] = (rules[line[0]][1], "+")
    return board, rules, boardSize, pieces


def generatePopulation(population, board, rules, pieces):
    # Creates a population with a little help from backtracking
    total = 0
    for i in range(100):
        # ADJUSTABLE: Can run more than 100 times, doesn't seem to make much of a difference
        solution = Solution(len(board))
        if backtrack0((0, 0), solution):
            solution.pieces = pieces
            solution.pieces = updatePieces(board, solution, rules)
            solution.fitness = getFitness(solution, board)
            population.append(solution)
            total += solution.fitness
    for i in range(len(population)):
        if population[i].fitness == 0:
            population[i].probability = 1
        population[i].probability = population[i].fitness/total
    return population


def updatePieces(board, solution, rules):
    # updates the pieces with all of their coordinates and values after the solution has been altered
    for x in range(len(board)):
        for y in range(len(board)):
            solution.pieces[board[x][y]].coords[(x, y)] = int(solution.grid[x][y])

    for key in solution.pieces.keys():
        operationIterator(rules[key], solution.pieces[key], solution.grid)
    return solution.pieces


def getFitness(solution, board):
    # calculates the fitness: row, column fitness are based on how many non-repeating
    # cells there are in each row, column. Piece fitness is the cells in all solved pieces.
    # the fitness is normalized to 1 by dividing by the number of cells, divided by 3
    grid = solution.grid

    rowFitness, colFitness, pieceFitness = 0, 0, 0
    for i in range(len(board)):
        rowCount = collections.Counter(grid[i])
        rowFitness += len(rowCount)
        col = [row[i] for row in grid]
        colCount = collections.Counter(col)
        colFitness += len(colCount)

    for piece in solution.pieces.values():
        if piece.isSolved:
            pieceFitness += len(piece.coords)
    fit = float(float(rowFitness + colFitness + pieceFitness)/float(3*len(board)**2))
    return fit


def operationIterator(rule, piece, solution):
    # checks which operation and performs said operation
    total = 0
    if len(piece.coords) < 2:
        return piece.coords.values()[0]

    operation = rule[1]
    vals = piece.coords.values()

    big = vals[0]
    small = vals[1]

    if big < small:
        big = vals[1]
        small = vals[0]

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
        for divisor in piece.coords.values():
            if not divisor == 0:
                if not float(rule[0]) % divisor == 0:
                    return 0

    if total == int(rule[0]):
        piece.isSolved = 1
    else:
        piece.isSolved = 0

    return np.abs(total - float(rule[0]))


def findRemainingValues(solution, coordinate, valuesToTry):
    grid = solution.grid
    # finds the values still available for use (no repeats)
    copyValuesToTry = valuesToTry[:]
    for num in range(1, len(grid) + 1):
        if findRepeats(grid, coordinate, num) > 0:
            copyValuesToTry.remove(num)
    return copyValuesToTry


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


def findRepeats(grid, coordinate, number):
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


def backtrack0(coordinate, solution):
    # just used to initially fill in each chromosome/solution with non-repeating rows and columns
    grid = solution.grid
    i = coordinate[0]
    j = coordinate[1]

    if i == len(grid) or j == len(grid):
        return 1

    valuesToTry = findRemainingValues(solution, coordinate, range(1, len(grid) + 1))
    np.random.shuffle(valuesToTry)
    if not len(valuesToTry):
        return 0

    for num in valuesToTry:
        grid[i][j] = num

        if num in valuesToTry:
            valuesToTry.remove(num)

        if j == len(grid) - 1:
            if backtrack0((i + 1, 0), solution):
                return 1
        else:
            if backtrack0((i, j + 1), solution):
                return 1

    grid[i][j] = 0
    return 0


def adjustingSwap(solution, board, rules):
    # tries to adjust a puzzle based on constraints
    # this is essentially a local search added on as a mutation, though I don't think it works very well, either.
    grid = solution.grid

    unsolved = []
    solved = []
    for key in solution.pieces.keys():
        if solution.pieces[key].isSolved == 0:
            unsolved.append(solution.pieces[key])
        else:
            solved.append(solution.pieces[key])

    if not unsolved:
        return solution

    if len(unsolved) > len(solved):
        # if there are more unsolved than solved pieces, a swap is conducted between pieces
        np.random.shuffle(unsolved)
        piece = unsolved[0]
        random = np.random.randint(0, len(piece.coords.keys()))

        swapFrom = piece.coords.keys()[random]  # randomly picks an unsolved piece
        i, j = swapFrom[0], swapFrom[1]

        swapi, swapj = i, np.random.randint(len(grid))  # generates a swap in the same row
        for r in range(len(grid)):
            if not (i, r) in piece.coords.keys() and \
                    not r == j and \
                    grid[i][r] in findPossibleValues(rules[piece.letter], range(1, len(grid)+1)):
                # checks that the swap is outside of the piece and that it's an "allowed" value based on math rules
                swapj = r
                justSwappedInRow = 1
                break
        if swapj == j:
            # indicates that there are no cells in a row for the piece, switching to check columns
            for r in range(len(grid)):
                if not (r, j) in piece.coords.keys() and \
                        not r == i and \
                        grid[r][j] in findPossibleValues(rules[piece.letter], range(1, len(grid)+1)):
                    swapi = r
                    justSwappedInRow = 0
                    break
    else:
        np.random.shuffle(solved)
        piece = solved[0]
        swapFrom = piece.coords.keys()[np.random.randint(0, len(piece.coords.keys()))]
        i, j = swapFrom[0], swapFrom[1]
        swapi, swapj = i, j
        if not len(piece.coords) == 1:
            for r in range(len(grid)):
                if (i, r) in piece.coords and not r == j:
                    swapj = r
                    justSwappedInRow = 1
                    break
            if swapj == j:
                for r in range(len(grid)):
                    if (r, j) in piece.coords and not r == i:
                        swapi = r
                        justSwappedInRow = 0
                        break

    iterations = 0

    temp = grid[i][j]
    swapTemp = grid[swapi][swapj]
    # values to be swapped

    grid[i][j] = swapTemp
    grid[swapi][swapj] = temp
    justSwappedInRow = 0
    # swapping
    while (checkForRepeats(solution) or iterations == 0) and iterations < 500:
        # tries to readjust the swap: swaps within a row, which means that columns are in violation. Swaps columns. Swaps rows, etc.
        # until an answer is reached or 500 iterations are reached.

        if justSwappedInRow == 1:
            transposedGrid = copy.deepcopy(grid).T
            col = transposedGrid[j]
            colToSwap = transposedGrid[swapj]
            justSwappedInRow = 0
            # get columns faster
        elif justSwappedInRow == 0:
            col = grid[i]
            colToSwap = grid[swapi]
            justSwappedInRow = 1

        colChecked, colToSwapChecked = 0, 0
        for r in range(len(grid)):
            if colChecked and colToSwapChecked:
                break
            if col[r] == swapTemp and colChecked == 0:
                if justSwappedInRow == 0:
                    if not r == i:
                        grid[r][j] = temp
                        i = r
                        colChecked = 1
                else:
                    if not r == j:
                        grid[i][r] = temp
                        j = r
                        colChecked = 1
            if colToSwap[r] == temp and colToSwapChecked == 0:
                if justSwappedInRow == 0:
                    if not r == swapi:
                        grid[r][swapj] = swapTemp
                        swapi = r
                        colToSwapChecked = 1
                else:
                    if not r == swapj:
                        grid[swapi][r] = swapTemp
                        swapj = r
                        colToSwapChecked = 1
        t = temp
        temp = swapTemp
        swapTemp = t

        iterations += 1
        updatePieces(board, solution, rules)
    return solution


class Piece:

    def __init__(self, letter):
        self.isSolved = 0
        self.letter = letter
        self.coords = {}
        self.cells = len(self.coords)


class Solution:

    def __init__(self, boardSize):
        self.fitness = 0
        self.probability = 0
        self.grid = np.zeros((boardSize, boardSize), dtype=int)
        self.pieces = []


x, fitness, y = solve()

row = ''
for a in range(0, len(x.grid)):
    for b in range(0, len(x.grid)):
        row = row + ' ' + str(x.grid[a][b])
    print row
    row = ''
print "Fitness (0 to 1, 1 being the best): " + str(fitness)
msg = "No solution was found, this was the best solution generated in {} iterations."
if not fitness == 1.0:
    print msg.format(y)



