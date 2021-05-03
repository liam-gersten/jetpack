import chunkGeneration
import random, copy

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
