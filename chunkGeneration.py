import pathfinders
import jetpack
import random, time, copy

class MiniChunk():  # small 2D list of a certain object
    def __init__(self, app, chunk, ranges, id):
        [self.literal, self.row, self.col] = [[], 0, 0]
        while True:  # keeps trying to make one that firs on the main chunk
            rows = random.randrange(ranges[0][0], ranges[0][1])
            cols = random.randrange(ranges[1][0], ranges[1][1])
            testList = []
            for r in range(rows):
                row = [id for i in range(cols)]
                testList += [row]
            row = random.randrange(2, app.rows-len(testList))
            col = random.randrange(2, app.cols-len(testList[0]))
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

def conversionWrapper(app, chunk):  # converts chunk values into booleans
    testChunk = []
    for r in range(len(chunk)):
        row = []
        for c in range(len(chunk[0])):
            if type(chunk[r][c]) == list: row += [False]
            else: row += [True]
        testChunk += [row]
    return pathfinders.pathFinder1(app, testChunk)

# places beams onto a test chunk and before testing with pathfinder
def beamGenerator(app, chunk, upperBeamRange, x):
    beamNumbers = [i for i in range(1, upperBeamRange+1)]
    while True:
        [tempBeams, tempChunk] = [[], copy.deepcopy(chunk)]
        for i in range(random.choice(beamNumbers)):
            beamChunk = MiniChunk(app, chunk, [[2, 5], [2, 5]], [])
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

# gets upperBeamRange from curves of time and difficulty value
def difficultyWrapper(app, chunk, x):
    difficultyCurves = {'easy': {'a': 5, 'b': 0},  # y = b + ax
            'medium': {'a': 4, 'b': 20}, 'hard': {'a': 6, 'b': 40}}
    curve = difficultyCurves[app.difficulty]
    difficulty = app.difficultyBase+(curve['a']*((time.time()-
                            app.timeInitial)/60))+curve['b']
    upperBeamRange = int(difficulty/20)+1  # second curve
    chunk = beamGenerator(app, chunk, upperBeamRange, x)
    return coinGenerator(app, chunk, x)

# makes blank 2D list to be called
def generationManager(app, x):
    bareChunk = []
    for r in range(app.rows):
        row = ['' for col in range(app.cols)]
        bareChunk += [row]
    return difficultyWrapper(app, bareChunk, x)
