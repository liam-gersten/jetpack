import pathfinders
import jetpack
import random, time, copy

class MiniChunk():
    def __init__(self, app, chunk, ranges, id):
        [self.literal, self.row, self.col] = [[], 0, 0]
        while True:
            rows = random.randrange(ranges[0][0], ranges[0][1])
            cols = random.randrange(ranges[1][0], ranges[1][1])
            testList = []
            for r in range(rows):
                row = [id for i in range(cols)]
                testList += [row]
            row = random.randrange(0, app.rows-len(testList))
            col = random.randrange(0, app.cols-len(testList[0]))
            if self.checkAvalibility(app, chunk, testList, row, col):
                [self.literal, self.row, self.col] = [testList, row, col]
                break

    def checkAvalibility(self, app, chunk, miniChunk, startRow, startCol):
        for row in range(len(miniChunk)):
            for col in range(len(miniChunk[0])):
                if (row+startRow >= app.rows) or (col+startCol >= app.cols) or \
                        (chunk[row+startRow][col+startCol] != ''):
                    return False
        return True

    def place(self, chunk, id):
        for row in range(len(self.literal)):
            for col in range(len(self.literal[0])):
                chunk[row+self.row][col+self.col] = id
        return chunk

def conversionWrapper(chunk):
    testChunk = []
    for r in range(len(chunk)):
        row = []
        for c in range(len(chunk[0])):
            if type(chunk[r][c]) == list: row += [False]
            else: row += [True]
        testChunk += [row]
    return True

def beamGenerator(app, chunk, upperBeamRange, x):
    beamNumbers = [i for i in range(1, upperBeamRange+1)]
    while True:
        tempBeams = []
        tempChunk = copy.deepcopy(chunk)
        for i in range(random.choice(beamNumbers)):
            beamChunk = MiniChunk(app, chunk, [[2, 5], [2, 5]], [])
            tempBeams += [beamChunk]
            tempChunk = beamChunk.place(tempChunk, [])
        if conversionWrapper(chunk):
            chunk = tempChunk
            for beamChunk in tempBeams:
                sizes = [len(beamChunk.literal), len(beamChunk.literal[0]),
                            beamChunk.row, beamChunk.col]
                type = random.choice([2, 3])
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

def coinGenerator(app, chunk, x):
    for i in range(random.randint(1, 2)):
        coinChunk = MiniChunk(app, chunk, [[2, 3], [2, 3]], 'c')
        for row in range(len(coinChunk.literal)):
            for col in range(len(coinChunk.literal[0])):
                app.coins += [jetpack.Coin(app, row+coinChunk.row,
                                           col+coinChunk.col, x)]
        chunk = coinChunk.place(chunk, 'c')
    return chunk

def difficultyWrapper(app, chunk, x):
    difficultyCurves = {'easy': {'a': 5, 'b': 0},
            'medium': {'a': 4, 'b': 20}, 'hard': {'a': 6, 'b': 40}}
    curve = difficultyCurves[app.difficulty]
    difficulty = (curve['a']*((time.time()-app.timeInitial)/60))+curve['b']
    upperBeamRange = int(difficulty/20)+1
    chunk = beamGenerator(app, chunk, upperBeamRange, x)
    return coinGenerator(app, chunk, x)

def generationManager(app, x):
    bareChunk = []
    for r in range(app.rows):
        row = ['' for col in range(app.cols)]
        bareChunk += [row]
    return difficultyWrapper(app, bareChunk, x)
