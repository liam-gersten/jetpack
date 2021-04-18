def drawBorders(x, app, canvas, color):
    for row in range(app.rows):
        for col in range(app.cols):
            x1 = x + (app.cellSize * col)
            y1 = app.cellSize * row
            x2 = x1 + app.cellSize
            y2 = y1 + app.cellSize
            canvas.create_rectangle(x1, y1, x2, y2, fill=color)

def printer(app):
    if type(app.currentChunk.literal) is list:
        print('\n**currentChunk**')
        print(app.currentChunk.x)
        for row in app.currentChunk.literal: print(row)
    if type(app.newChunk.literal) is list:
        print('\n**newChunk**')
        print(app.newChunk.x)
        for row in app.newChunk.literal: print(row)
    if app.beams != []:
        print('\n**beams**')
        for beam in app.beams:
            print('\n')
            print(beam.x1, beam.y1, beam.x2, beam.y2)

def outlineScotty(object, canvas):
    canvas.create_rectangle(object.x-(object.sizeX/2), object.y-
        (object.sizeY/2), object.x+(object.sizeX/2), object.y+(object.sizeY/2),
                            fill='')

def tp0ReadMe():
    print('\n**Tp0 Description**\n')
    print('Main game stored in jetpack.py (see instructions below)')
    print('Debugging and write up functions stored in debugger.py')
    print('As of now, the project requires no module installation')
    print('Numerous images are stored in the sprites folder')
    print('All images are original works by me (more are in the works)')
    print('\n**Instructions**\n')
    print('Hold mouse/touchpad to make Scotty fly')
    print('Use the arrow keys to increase/decrease game speed')
    print('Pressing R restarts the game')
    print('Pressing P pauses the game (some animations persist)')
    print('Pressing D activates debugger mode')
    print('Pressing C prints object information and lists')
