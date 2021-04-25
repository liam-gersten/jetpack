import time
import random
from cmu_112_graphics import *

def getMovesByQuadrant(row, col, drow, dcol):
    pass

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

# Tests

def checkAvalibility(miniChunk, startRow, startCol, chunk):
    for row in range(len(miniChunk)):
        for col in range(len(miniChunk[row])):
            if (row+startRow >= 20) or (col+startCol >= 40) or \
                    (chunk[row+startRow][col+startCol] == [1]):
                return False
    return True

def testAlgorithms(trials):
    [v1, v2, v3, v4] = [[], [], [], []]
    for trial in range(trials):
        chunk = None
        timeInitial = time.time()+0
        # versionOne(chunk, 10, 0, 0, 1, True)
        v1.append(time.time()-timeInitial)
        # timeInitial = time.time()+0
        # versionTwo(chunk)
        # v2.append(time.time()-timeInitial)

# testAlgorithms(50)

def appStarted(app):
    [app.rows, app.cols] = [20, 40]
    app.cellSize = app.width/app.cols
    restartApp(app)

def restartApp(app):
    app.chunk = None
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
