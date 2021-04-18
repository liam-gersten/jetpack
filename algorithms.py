import time
import random
from cmu_112_graphics import *

def getMovesByQuadrant(row, col, drow, dcol):
    if row <= 9:
        if row <= 1: return [[1, 1], [0, 1], [-1, 1]]
        return [[0, 1], [1, 1], [-1, 1]]
    if row >= 19: return [[-1, 1], [0, 1], [1, 1]]
    return [[0, 1], [0, 1], [1, 1]]

# Version One

def versionOneHelper():
    pass

def versionOne(chunk, row, col, drow, dcol, moveNext):
    pass

# Version Two

def versionTwoHelper():
    pass

def versionTwo(chunk):
    pass

# Version Three

def versionThreehelper():
    pass

def versionThree(chunk):
    pass

# Version Four

def versionFourHelper():
    pass

def versionFour(chunk):
    pass

# Tests

def checkAvalibility(miniChunk, startRow, startCol, chunk):
    for row in range(len(miniChunk)):
        for col in range(len(miniChunk[row])):
            if (row+startRow >= 20) or (col+startCol >= 40) or \
                    (chunk[row+startRow][col+startCol] == [1]):
                return False
    return True

def generateBeamChunk(ranges, emptyChunk, mainChunk):
    loopNumber = 0
    while True:
        emptyChunk = []
        if loopNumber > 50: return False
        [rows, cols] = [random.randrange(ranges[1][0], ranges[1][1]),
                        random.randrange(ranges[0][0], ranges[0][1])]
        for row in range(rows):
            currentRow = []
            for col in range(cols): currentRow += [[1]]
            emptyChunk.append(currentRow)
        [row, col] = [random.randint(0, 20-1),
                      random.randint(5, 40-1)]
        if checkAvalibility(emptyChunk, row, col, mainChunk): break
        loopNumber += 1
    return [emptyChunk, row, col]

def modifyBoard(miniChunk, storeList, version, mainChunk):
    for row in range(len(miniChunk[0])):
        for col in range(len(miniChunk[0][0])):
            if version == []: object = [1]
            mainChunk[row+miniChunk[1]][col+miniChunk[2]] = object

def generateChunk():
    chunk = []
    for r in range(20):
        row = []
        for col in range(40): row += [0]
        chunk.append(row)
    for b in range(random.choice([2, 3, 4, 5])):
        beamChunk = generateBeamChunk([[1, 6], [1, 6]], [], chunk)
        if not beamChunk: break
        modifyBoard(beamChunk, [], [], chunk)
    return chunk

def testAlgorithms(trials):
    [v1, v2, v3, v4] = [[], [], [], []]
    for trial in range(trials):
        chunk = generateChunk()
        timeInitial = time.time()+0
        # versionOne(chunk, 10, 0, 0, 1, True)
        v1.append(time.time()-timeInitial)
        # timeInitial = time.time()+0
        # versionTwo(chunk)
        # v2.append(time.time()-timeInitial)
        # timeInitial = time.time()+0
        # versionThree(chunk)
        # v3.append(time.time()-timeInitial)
        # timeInitial = time.time()+0
        # versionFour(chunk)
        # v4.append(time.time()-timeInitial)

# testAlgorithms(50)

def appStarted(app):
    [app.rows, app.cols] = [20, 40]
    app.cellSize = app.width/app.cols
    restartApp(app)

def restartApp(app):
    app.chunk = generateChunk()
    # versionOne(app.chunk, 10, 0, 0, 1, True)

def keyPressed(app, event):
    if event.key.lower() == 'r': restartApp(app)

def redrawAll(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.chunk[row][col] == [1]: color = 'red'
            elif app.chunk[row][col] == 1: color = 'blue'
            else: color = 'white'
            [x1, y1] = [col * app.cellSize, row * app.cellSize]
            [x2, y2] = [x1 + app.cellSize, y1 + app.cellSize]
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=5)

if __name__ == '__main__':
    runApp(width=1000, height=500)
