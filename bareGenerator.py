import random, copy

########
# This file is partially duplicated code from chunkGeneration.py for testing
# purposes only. It should not count towards TP1
########

class DummyApp():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

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