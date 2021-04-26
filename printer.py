import matplotlib.pyplot as plt  # used only for testing purposes

def drawBorders(x, app, canvas, color):  # displays chunk cells and borders
    for row in range(app.rows):
        for col in range(app.cols):
            x1 = x+(app.cellSize*col)
            y1 = app.cellSize*row
            x2 = x1+app.cellSize
            y2 = y1+app.cellSize
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

def tp1ReadMe():  # instructions as of tp1
    print('\n**Instructions**\n')
    print('Hold mouse/touchpad to make Scotty fly')
    print('Use the arrow keys to increase/decrease game speed')
    print('Pressing R restarts the game')
    print('Pressing P pauses the game (some animations persist)')
    print('Pressing D activates debugger mode')
    print('Pressing C prints object information and lists')
