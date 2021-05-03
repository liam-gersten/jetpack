import chunkGeneration
import random, copy, time
import matplotlib.pyplot as plt  # used only for testing purposes

######
# Printer/Debugger code
######

def printData(app):
    print(app.missileAvoids)
    print(app.missileDeaths)
    print(app.beamDeathQuadrants)
    print(app.beamDeathTypes)
    print('\n')
    dist1 = chunkGeneration.mergeSingleDistribution(25, app.missileAvoids,
                                                    'missile')
    dist2 = chunkGeneration.mergeSingleDistribution(25, app.missileDeaths,
                                                    'missile')
    print(dist1)
    print(dist2)
    print(chunkGeneration.mergeDoubleDistributions(100, dist2, dist1))
    print(chunkGeneration.mergeSingleDistribution(25, app.beamDeathQuadrants,
                                                  'beam'))
    print(chunkGeneration.mergeSingleDistribution(25, app.beamDeathTypes,
                                                  'beam'))
    print('\n')

def drawBorders(x, app, canvas, color):  # displays chunk cells and borders
    for row in range(app.rows):
        for col in range(app.cols):
            x1 = x+(app.cellSize*col)
            y1 = app.barY+app.cellSize*row
            x2 = x1+app.cellSize
            y2 = app.barY+y1+app.cellSize
            canvas.create_rectangle(x1, y1, x2, y2, fill=color)

def printer(app):  # prints new and current chunks
    if type(app.currentChunk.literal) is list:
        print('\n**currentChunk**')
        print(app.currentChunk.x)
        for row in app.currentChunk.literal: print(row)
    if type(app.newChunk.literal) is list:
        print('\n**newChunk**')
        print(app.newChunk.x)
        for row in app.newChunk.literal: print(row)

def histogram(list1, list2, color):
    n, bins, patches = plt.hist(list1, len(list1), facecolor=color)
    if list2: n, bins, patches = plt.hist(list2, len(list2), facecolor='red')
    plt.show()

def outlineScotty(object, canvas):  # displays the hitbox for scotty
    canvas.create_rectangle(object.x-(object.sizeX/2), object.y-
        (object.sizeY/2), object.x+(object.sizeX/2), object.y+(object.sizeY/2),
                            fill='')

def tp3ReadMe():  # instructions as of tp1
    pass

######
# bareGenerator code
######

class DummyApp():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.lazyGeneration = False

class MiniChunk():
    def __init__(self, chunk, ranges, id, approws, appcols):
        [self.literal, self.row, self.col] = [[], 0, 0]
        while True:
            rows = random.randrange(ranges[0][0], ranges[0][1])
            cols = random.randrange(ranges[1][0], ranges[1][1])
            testList = []
            for r in range(rows):
                row = [id for i in range(cols)]
                testList += [row]
            row = random.randrange(0, approws-len(testList))
            col = random.randrange(0, appcols-len(testList[0]))
            if self.checkAvalibility(chunk, testList, row, col, rows, cols):
                [self.literal, self.row, self.col] = [testList, row, col]
                break

    def checkAvalibility(self, chunk, miniChunk, startRow, startCol, rows, cols):
        for row in range(len(miniChunk)):
            for col in range(len(miniChunk[0])):
                if (row+startRow >= (len(chunk))) or \
                        (col+startCol >= len(chunk[0])) or \
                        (chunk[row+startRow][col+startCol] != ''):
                    return False
        return True

    def place(self, chunk, id):
        for row in range(len(self.literal)):
            for col in range(len(self.literal[0])):
                chunk[row+self.row][col+self.col] = id
        return chunk

def beamGenerator(chunk, rows, cols, upperBeamRange):
    beamNumbers = [i for i in range(1, upperBeamRange+1)]
    while True:
        tempChunk = copy.deepcopy(chunk)
        for i in range(random.choice(beamNumbers)):
            beamChunk = MiniChunk(chunk, [[2, 5], [2, 5]], [], rows, cols)
            tempChunk = beamChunk.place(tempChunk, [])
        return tempChunk

def difficultyWrapper(chunk, rows, cols, upperBeamRange):
    return beamGenerator(chunk, rows, cols, upperBeamRange)

def generator(rows, cols, upperBeamRange):
    bareChunk = []
    for r in range(rows):
        row = ['' for col in range(cols)]
        bareChunk += [row]
    return difficultyWrapper(bareChunk, rows, cols, upperBeamRange)

######
# Pathfinder test Code
######

def displayResults(outerV1, outerV2, v1Pairs, v2Pairs):
    histogram(outerV1, outerV2, 'blue')
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
            for upperBeamRange in range(2, 12):
                [v1, v2] = [[], []]
                for trial in range(trials):
                    chunk = generator(rows, cols, upperBeamRange)
                    timeInitial = time.time()+0
                    value = chunkGeneration.conversionWrapper(app, chunk)
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
    histogram(outerV1, False, 'blue')
    histogram(outerV1, False, 'red')
    displayResults(outerV1, outerV2, v1Pairs, v2Pairs)

def runTests():
    [trials, variations] = [50, 2]
    [rows, cols] = [20, 40]
    app = DummyApp(rows, cols)
    testAlgorithms(trials, variations, rows, cols, app)

######
# Dead code (used for reference)
######

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

if (__name__ == '__main__'):
    runTests()
