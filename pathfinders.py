import bareGenerator
import chunkGeneration
import time, random, math
import matplotlib.pyplot as plt
from cmu_112_graphics import *

# gets auto sequence of searches to make for one of 4 quadrants
def getMovesByQuadrant(app, row):
    if row <= app.rows//2:
        if row <= app.rows//4: return [[1, 1], [0, 1], [-1, 1]]
        return [[0, 1], [1, 1], [-1, 1]]
    if row <= 3*app.rows//4: return [[0, 1], [-1, 1], [1, 1]]
    return [[-1, 1], [0, 1], [1, 1]]

def checkFour(app, chunk, row, col):  # checks space for 2x2 scotty
    for r in range(2):
        for c in range(2):
            if (row+r < 0) or (app.rows <= row+r) or (col+c < 0): return False
            if col+c >= app.cols-1: return True
            if not chunk[row+r][col+c]: return False
    return True

def pathFinder1(app, chunk):  # pathfinder1's wrapper
    for startRow in range(0, app.rows-1, 2):
        if modifiedDepthFirst(app, chunk, startRow, 0): return True
    return False

def memorizeDFS(searcher):  # cache helper for modifiedDepthFirst
    import functools
    cachedResults = dict()
    @functools.wraps(searcher)
    def wrapper(*args):
        if str(args) not in cachedResults:
            cachedResults[str(args)] = searcher(*args)
        return cachedResults[str(args)]
    return wrapper

@memorizeDFS
def modifiedDepthFirst(app, chunk, row, col):
    if not checkFour(app, chunk, row, col): return False
    if col == app.cols-1: return True  # reached end
    moves = getMovesByQuadrant(app, row)
    for sequence in moves:
        [testRow, testCol] = [row+sequence[0], col+sequence[1]]
        if modifiedDepthFirst(app, chunk, testRow, testCol): return True
    return False

def pathFinder2(app, chunk):  # pathfinder2's wrapper
    for startRow in range(0, app.rows-1, 2):
        if nonGuidedHalfPoint(app, chunk, startRow, 0): return True
    return False

def memorizeHP(searcher): # cache helper for nonGuidedHalfPoint
    import functools
    cachedResults = dict()
    @functools.wraps(searcher)
    def wrapper(*args):
        if str(args) not in cachedResults:
            cachedResults[str(args)] = searcher(*args)
        return cachedResults[str(args)]
    return wrapper

@memorizeHP
def nonGuidedHalfPoint(app, chunk, row, col):
    pass

def testCaller(version, app, chunk):
    if version == 1: return pathFinder1(app, chunk)
    return pathFinder1(app, chunk)

def displayResults(outerV1, outerV2, v1Pairs, v2Pairs):
    n, bins, patches = plt.hist(outerV1, len(outerV1), facecolor='blue')
    n, bins, patches = plt.hist(outerV2, len(outerV2), facecolor='blue')
    plt.show()
    for listColor in [[v1Pairs, 'blue'], [v2Pairs, 'red']]:
        [x, y] = [[], []]
        for pair in listColor[0]:
            x.append(pair[0])
            y.append(pair[1])
        plt.scatter(x, y, c=listColor[1])
    plt.show()

def testAlgorithms(trials, variations, rows, cols, app):
    [outerV1, outerV2] = [[], []]
    [v1Pairs, v2Pairs] = [[], []]
    for version in range(1, 3):
        for i in range(variations):
            print(i)
            for upperBeamRange in range(2, 30):
                [v1, v2] = [[], []]
                for trial in range(trials):
                    chunk = bareGenerator.generator(rows, cols, upperBeamRange)
                    timeInitial = time.time()+0
                    value = pathFinder1(app,
                                chunkGeneration.conversionWrapper(app, chunk))
                    timeCompleted = time.time()-timeInitial
                    if version == 1:
                        v1.append(timeCompleted)
                        outerV1.append(timeCompleted)
                    else:
                        v2.append(timeCompleted)
                        outerV2.append(timeCompleted)
                if version == 1:
                    v1Pairs.append([upperBeamRange, sum(v1)/len(v1)])
                else: v2Pairs.append([upperBeamRange, sum(v2)/len(v2)])
    displayResults(outerV1, outerV2, v1Pairs, v2Pairs)

if __name__ == '__main__':
    trials = 50
    variations = 3
    [rows, cols] = [20, 40]
    app = bareGenerator.DummyApp(rows, cols)
    testAlgorithms(trials, variations, rows, cols, app)
