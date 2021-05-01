import jetpack
import random, copy, time

class MiniChunk():  # small 2D list of a certain object
    def __init__(self, app, chunk, ranges, id):
        [self.literal, self.row, self.col] = [[], 0, 0]
        while True:  # keeps trying to make one that firs on the main chunk
            rows = random.randrange(ranges[0][0], ranges[0][1])
            cols = random.randrange(ranges[1][0], ranges[1][1])
            if not (id == [] and ([rows, cols] == [2, 2])):
                testList = []
                for r in range(rows):
                    row = [id for i in range(cols)]
                    testList += [row]
                if app.firstChunk: firstCol = app.cols/2
                else: firstCol = 3
                row = random.randrange(0, app.rows-len(testList))
                col = random.randrange(firstCol, app.cols-len(testList[0]))
                if self.checkAvalibility(app, chunk, testList, row, col):
                    [self.literal, self.row, self.col] = [testList, row, col]
                    break  # ready to place on the main test chunk

    # fits properly within the test chunk
    def checkAvalibility(self, app, chunk, miniChunk, startRow, startCol):
        for row in range(len(miniChunk)):
            for col in range(len(miniChunk[0])):
                if (row+startRow >= app.rows) or (col+startCol >= app.cols) or \
                        (chunk[row+startRow][col+startCol] != ''):
                    return False
        return True

    def place(self, chunk, id):  # places self.literal onto the test chunk
        for row in range(len(self.literal)):
            for col in range(len(self.literal[0])):
                chunk[row+self.row][col+self.col] = id
        return chunk

def biasDicts(app):
    app.missileAvoids = {0: 0, 1: 0, 2: 0, 3: 0}
    app.missileDeaths = {0: 0, 1: 0, 2: 0, 3: 0}
    app.beamDeathQuadrants = {0: 0, 1: 0, 2: 0, 3: 0}
    app.beamDeathTypes = {'static': 0, 'vertical': 0, 'horizontal': 0,
                          'rotating': 0}

def getQuadrantFromY(app, y):
    if y <= (app.barY+(app.trueHeight/2)):
        if y <= (app.barY+(app.trueHeight/4)): return 0
        return 1
    if y <= (app.barY+((3*app.trueHeight)/4)): return 2
    return 3

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

def pathFinder(app, chunk):  # pathfinder1's wrapper
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

def conversionWrapper(app, chunk):  # converts chunk values into booleans
    if app.lazyGeneration: return True
    testChunk = []
    for r in range(len(chunk)):
        row = []
        for c in range(len(chunk[0])):
            if type(chunk[r][c]) == list: row += [False]
            else: row += [True]
        testChunk += [row]
    return pathFinder(app, testChunk)

def mergeDoubleDistributions(difficulty, dist1, dist2):
    avoidanceWeight = (1/10)+(difficulty/250)
    deathWeight = (1-avoidanceWeight)*100
    avoidanceWeight *= 100
    newProportions = {}
    for key in dist1:
        [p1, p2] = [dist1[key], dist2[key]]
        newProportions[key] = ((deathWeight*p1)+(avoidanceWeight*p2))/100
    return newProportions

def mergeSingleDistribution(difficulty, distribution, type):
    totalPossible = 0
    if type == 'missile': biasWeight = difficulty/50
    else: biasWeight = difficulty/100
    newProportions = {}
    originalWeight = (1-biasWeight)*100
    biasWeight *= 100
    for key in distribution: totalPossible += distribution[key]
    for key in distribution:
        p1 = distribution[key]/totalPossible
        p2 = 0.25
        newProportions[key] = ((biasWeight*p1)+(originalWeight*p2))/100
    return newProportions

def createDistribution(app, difficulty, type):
    [distribution, distributionSize] = [[], 30]
    probabilities = mergeSingleDistribution(difficulty, app.beamDeathTypes,
                                            type)
    for key in probabilities:
        number = int(probabilities[key]*distributionSize)
        for i in range(number):
            distribution += [key]
    return distribution

# places beams onto a test chunk and before testing with pathfinder
def beamGenerator(app, chunk, upperBeamRange, x):
    beamNumbers = [i for i in range(1, upperBeamRange+1)]
    while True:
        [tempBeams, tempChunk] = [[], copy.deepcopy(chunk)]
        for i in range(random.choice(beamNumbers)):
            beamChunk = MiniChunk(app, chunk, [[2, 9], [2, 9]], [])
            tempBeams += [beamChunk]  # objects help until tested
            tempChunk = beamChunk.place(tempChunk, [])
        if conversionWrapper(app, tempChunk):  # pathfinder returns True
            chunk = tempChunk
            for beamChunk in tempBeams:  # one of four beam types created
                sizes = [len(beamChunk.literal), len(beamChunk.literal[0]),
                            beamChunk.row, beamChunk.col]
                if sizes[0] == sizes[1]: type = 4
                else: type = random.choice([1, 2, 3])
                if type == 1: object = jetpack.staticBeam(app, sizes[0],
                                        sizes[1], sizes[2], sizes[3], x)
                elif type == 2: object = jetpack.verticleBeam(app, sizes[0],
                                        sizes[1], sizes[2], sizes[3], x)
                elif type == 3: object = jetpack.horizontalBeam(app, sizes[0],
                                        sizes[1], sizes[2], sizes[3], x)
                else: object = jetpack.rotatingBeam(app, sizes[0], sizes[1],
                                                sizes[2], sizes[3], x)
                app.beams += [object]
            return chunk

# places coin chunks onto the final chunk (already verified by pathfinder)
def coinGenerator(app, chunk, x):
    for i in range(random.randint(1, 3)):  # range of coin chunks
        coinChunk = MiniChunk(app, chunk, [[2, 3], [2, 3]], 'c')
        for row in range(len(coinChunk.literal)):
            for col in range(len(coinChunk.literal[0])):
                app.coins += [jetpack.Coin(app, row+coinChunk.row,
                                           col+coinChunk.col, x, False)]
        chunk = coinChunk.place(chunk, 'c')
    return chunk

def missileGenerator(app, difficulty, byPass):  # spawns missiles
    if not byPass:  # makes a distribution for random selection
        missileProbability = ((3*difficulty)/800)+(1/8)
        perfectDistribution = []
        for i in range(int(missileProbability*10)): perfectDistribution += [1]
        for i in range(10-int(missileProbability*10)):
            perfectDistribution += [0]
    if byPass or (random.choice(perfectDistribution) == 1):
        missileSize = app.missile.size[1]/2
        y = random.randrange(int(app.barY+missileSize),
                             int(app.height-missileSize))
        waitTime = ((3*difficulty)/100)+1
        app.warnings += [jetpack.Exclamation(app, y, waitTime)]

def getNewRowCol(chunk):  # helper for powerUpGenerator that chooses row and col
    while True:
        [row, col] = [random.randint(1, len(chunk)-2),
                      random.randint(0, len(chunk[0])-1)]
        if chunk[row][col] == '':
            chunk[row][col] = 'c'
            return [row, col]

def powerUpGenerator(app, chunk):  # spawns power ups on top of chunks
    choice = random.choice([1, 1, 2, 2, 3, 0, 0, 0, 0, 0, 0, 0])
    if choice != 0: [row, col] = getNewRowCol(chunk)
    if choice == 1: app.powerUps += [jetpack.TimeSlower(app, (col*app.cellSize)+
        (app.cellSize/2), app.barY+(row*app.cellSize)+(app.cellSize/2))]
    elif choice == 2: app.powerUps += [jetpack.Invincibility(app, (col*
        app.cellSize)+(app.cellSize/2), app.barY+(row*app.cellSize)+
                                                (app.cellSize/2))]
    elif choice == 3: app.powerUps += [jetpack.Booster(app, (col*app.cellSize)+
        (app.cellSize/2), app.barY+(row*app.cellSize)+(app.cellSize/2))]

# gets upperBeamRange from curves of time and difficulty value
def difficultyWrapper(app, chunk, x):
    difficultyCurves = {'easy': {'a': 5, 'b': 0},  # y = b + ax
            'medium': {'a': 4, 'b': 20}, 'hard': {'a': 6, 'b': 40}}
    curve = difficultyCurves[app.difficulty]
    difficulty = app.difficultyBase+(curve['a']*((time.time()-
                            app.timeInitial)/60))+curve['b']
    app.speed = app.scale*(2+((difficulty*1)/10))/app.timeDilation
    if app.lazyGeneration: upperBeamRange = 3
    upperBeamRange = int(difficulty/20)+1  # second curve
    if not app.invincible: missileGenerator(app, difficulty, False)
    chunk = beamGenerator(app, chunk, upperBeamRange, x)
    # if not app.powerUp: powerUpGenerator(app, chunk)
    return coinGenerator(app, chunk, x)

def generationManager(app, x): # makes blank 2D list to be called
    bareChunk = []
    for r in range(app.rows):
        row = ['' for col in range(app.cols)]
        bareChunk += [row]
    return difficultyWrapper(app, bareChunk, x)
