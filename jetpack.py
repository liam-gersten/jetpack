from cmu_112_graphics import *
import testCode
import chunkGeneration
from PIL import Image
import math, time, random, copy

def almostEqual(d1, d2, epsilon=10**-7): return (abs(d2-d1) < epsilon)

# vector calculus for min distance between point and line
def minDistance(pa, pb, px):
    abVector = [pb[0]-pa[0], pb[1]-pa[1]]
    beVector = [px[0]-pb[0], px[1]-pb[1]]
    axVector = [px[0]-pa[0], px[1]-pa[1]]
    dotABBX = (abVector[0]*beVector[0])+(abVector[1]*beVector[1])
    dotABAX = (abVector[0]*axVector[0])+(abVector[1]*axVector[1])
    if (dotABBX > 0): return math.sqrt(((px[0]-pb[0])**2)+((px[1]-pb[1])**2))
    elif (dotABAX < 0): return math.sqrt(((px[0]-pa[0])**2)+((px[1]-pa[1])**2))
    else: return abs(((abVector[0])*(axVector[1]))-((abVector[1])*
                (axVector[0])))/(math.sqrt(((abVector[0])**2)+(abVector[1]**2)))

def drawBeam(app, canvas, x1, y1, x2, y2):  # works for all beam typea
    if (x1 > app.width) and (x2 > app.width): return None
    color = 'red'
    width = random.choice([11, 5, 12, 8, 10, 6])  # beam widths
    if app.timeDilation == 3: color ='spring green' # slowed time
    elif app.invincible: [color, width] = ['white', 5]
    scaleColor = [[3, 'grey50'], [10, color]]  # scales
    canvas.create_line(x1, y1, x2, y2, fill=color, width=width*app.scale)
    for coords in [[x1, y1], [x2, y2]]:
        for scale in scaleColor: canvas.create_oval(coords[0]-(
                app.cellSize/scale[0]),coords[1]-(app.cellSize/scale[0]),
                coords[0]+(app.cellSize/scale[0]),
            coords[1]+(app.cellSize/scale[0]), fill=scale[1])
    if app.timeDilation == 3: canvas.create_image(x1+((x2-x1)/2),  # clock
                y1+((y2-y1)/2), image=ImageTk.PhotoImage(app.clock))

def managePowerUp(object, app):  # manages power ups of any type
    if (not object.active) and (object.x+object.sprite.size[0] < 0):return False
    elif not object.active:
        object.x -= app.speed
        if math.sqrt(((object.x-app.player.x)**2)+((object.y-app.player.y)**2))\
                <= (app.player.sizeX): object.activate(app)
    elif time.time()-object.timeInitial >= object.timeLength:
        object.deactivate(app)
        return True
    return False

def drawPowerUp(object, app, canvas):  # draws power ups of any type
    heightChange = 5
    if object.x-app.cellSize > app.width: return None
    if not object.active: yChange = heightChange*math.sin(heightChange*
                                    time.time())*app.scale
    else: yChange = 0
    canvas.create_image(object.x, object.y+yChange,
                        image=ImageTk.PhotoImage(object.sprite))
    if object.active:
        if object.frozen: timer = int(object.timeLength-(object.timePaused-
                                                         object.timeInitial))
        else: timer = int(object.timeLength-(time.time()-object.timeInitial))
        if timer <= 5: color = 'red'
        else: color = 'black'
        font = 'Times', str(int(24*app.scale)), 'bold italic'
        canvas.create_text(object.x+app.barY, object.y, fill=color,
                           text=timer, anchor='center', font=font)

def pauseGame(app):  # pauses game and freezes all objects
    app.paused = not app.paused
    if app.paused: app.timePaused = time.time()
    else: app.pausedTime += (time.time()-app.timePaused)
    for warning in app.warnings: warning.freeze(app.paused)
    for beam in app.beams:
        if beam.type != 'static': beam.freeze(app.paused)
    for powerUp in app.powerUps:
        if powerUp.active: powerUp.freeze(app.paused)

class Scotty():  # class for player
    def __init__(self, app, images, igniteImages):
        self.x = app.width/4  # specific x coordinate
        self.y = 427*app.scaleY  # specific y coordinate
        [self.sizeX, self.sizeY] = [52*app.scale, 36*app.scale]  # sprite sizes
        [self.up, self.airborne, self.fireStart] = [False, False, False]
        self.freezeFactor = 1
        self.images = images
        self.igniteImages = igniteImages
        [self.changeX, self.changeY] = [0, 0]

    def move(self, app, changeY):  # shakes when rising:
        if self.up: self.changeX = random.choice([-1, 0, 1])
        else: self.changeX = 0
        if app.barY+self.sizeY/2 < self.y+changeY < (app.height-(self.sizeY/2)):
            self.y += changeY/self.freezeFactor  # within bounds of game
        elif self.y+changeY >= app.height-(self.sizeY/2):
            self.airborne = False  # now running on the ground
            self.y = app.height-(self.sizeY/2)-(5*app.scale)
            [self.sizeX, self.sizeY] = [52*app.scale, 36*app.scale]
        if self.y+(self.sizeY/2) > app.height:
            self.y = app.height-(self.sizeY/2)

    def manage(self):
        if self.freezeFactor != 1:
            self.changeY = random.choice([-2, -1, 0, 1, 2])  # shakes
            if (int((time.time()-self.fireStart)*10))/10 > 0.5:
                self.fireStart = time.time()  # 1 second curve
        else: self.changeY = 0

    def draw(self, app, canvas, debug):
        if (self.airborne or self.up): key = -1
        elif app.paused or (not app.start): key = 0
        else: key = int((time.time()*7*(app.speed/5))%3)  # specific key curve
        image = ImageTk.PhotoImage(self.images[key])
        if self.freezeFactor != 1: image = ImageTk.PhotoImage(self.images[-2])
        canvas.create_image(self.x+self.changeX, self.y+self.changeY,
                            image=image)
        if debug: testCode.outlineScotty(self, canvas)
        if (app.invincible) and (self.freezeFactor == 1): canvas.create_image(
            self.x, self.y, image=ImageTk.PhotoImage(app.miniHeart))

    def drawFire(self, app, canvas):
        if self.up and (self.freezeFactor == 1): self.drawNormal(app, canvas)
        elif self.freezeFactor != 1: self.drawBlue(app, canvas)

    def drawNormal(self, app, canvas): # standard red fire
        startCoords = [self.x-(12*app.scale), self.y+(self.sizeY/2)]  # sprite
        key = (int((time.time()-app.upInitial)*10))/10  # 1 second curve
        if key > 1.8: key = random.choice([1.5, 1.6, 1.7, 1.8])  # extra keys
        image = ImageTk.PhotoImage(self.igniteImages[key])
        y = startCoords[1]+((self.igniteImages[key].size[1])/2)
        canvas.create_image(startCoords[0]+self.changeX, y, image=image)

    def drawBlue(self, app, canvas):  # draws fire during super speed
        key = (int((time.time()-self.fireStart)*10))/10  # 1 second curve
        if key > 0.5: key = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])
        image = ImageTk.PhotoImage(app.rightFire[key])
        x = self.x-(self.images[-2].size[0]/2)-(app.rightFire[key].size[0]/2)
        canvas.create_image(x, self.y-(12*app.scale)+self.changeY, image=image)

class BackDrop():  # single sprite of Cohon University Center
    def __init__(self, app, index, x, type):
        self.type = type
        if self.type != 2:  # standard sprites
            if x: self.x = x
            elif not app.start: self.x = app.dropImages[2].size[0]+\
                (app.dropSize[0]/2)+(index*app.dropSize[0])
            else: self.x = (app.dropSize[0]/2)+(index*app.dropSize[0])
            self.y = app.height-(app.dropSize[1]/2)+app.dropY
            self.key = random.choice([0, 1])
            self.image = app.getCachedPhotoImage(app.dropImages[self.key])
        else:  # front of Cohon at start
            self.image = app.getCachedPhotoImage(app.dropImages[2])
            self.x = app.dropImages[2].size[0]/2
            self.y = app.height-(app.dropImages[2].size[1]/2)

    def move(self, app): self.x -= app.speed/app.dropMultiplier

    def draw(self, app, canvas): canvas.create_image(self.x, self.y,
                                            image=self.image)

class Coin():  # spinning coin object
    def __init__(self, app, row, col, chunkX, special):
        if not special:  # normal coins
            self.special = False
            self.x = chunkX+(app.cellSize*col)+\
                     ((app.coinSize+app.coinSpacing)/2)
            self.y = app.barY+(app.cellSize*row)+\
                     ((app.coinSize+app.coinSpacing)/2)
        else:  # spinning coin in the upper left
            self.special = True
            self.standardSize = app.buttonSizes/app.coinSequence[0].size[0]
            self.x = (app.buttonSizes/2)+app.buttonSpacing
            self.y = app.barY/2

    def changeTimeState(self, app):  # creates endless loops
        if time.time()-app.coinStart >= 1: app.coinStart = False

    def interacts(self, x, y, distance):  # player touches
        if math.sqrt(((self.x-x)**2)+((self.y-y)**2)) <= distance: return True
        return False

    def draw(self, app, canvas, debug, sequence, size):
        coinId = int((time.time()*10)%7)  # ranges 0 - 6
        if not self.special: image = app.getCachedPhotoImage(sequence[coinId])
        else:  # coin is in the top left of the menu bar
            if app.coinStart: sizeScale = \
            self.standardSize*(1+math.sin(math.pi*(time.time()-app.coinStart)))
            else: sizeScale = self.standardSize
            image = app.getCachedPhotoImage(
                app.scaleImage(sequence[coinId], sizeScale))
        canvas.create_image(self.x, self.y, image=image)
        if debug: canvas.create_rectangle(self.x-(size/2), self.y-(size/2),
                self.x+(size/2), self.y+(size/2), fill='')

class StaticBeam():  # does not move
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.type = 'static'
        self.width = app.cellSize
        if (rows == 1) or (cols == 1): [minus, first, second] = [1, 0, 0]
        else:  # diagonal
            minus = 0
            [first, second] = random.choice([[[rows-1, 0], [0, cols-1]],
                                             [[0, 0], [rows-1, cols-1]]])
        self.x1 = ((col+first[1])*app.cellSize)+chunkX+(app.cellSize/2)
        self.y1 = ((row+first[0])*app.cellSize)+(app.cellSize/2)+app.barY
        self.x2 = ((col+second[1]-minus)*app.cellSize)+chunkX+(app.cellSize/2)
        self.y2 = ((row+second[0]-minus)*app.cellSize)+(app.cellSize/2)+app.barY

    def move(self, app):  # used for inheritance
        self.x1 -= app.speed
        self.x2 -= app.speed

    def outOfBounds(self): return (self.x1+(self.width/3) < 0) and \
                                  (self.x2+(self.width/3) < 0)

    def interacts(self, app, player): return minDistance([self.x1, self.y1],
                [self.x2, self.y2], [player.x, player.y]) <= (player.sizeX/2)

    def draw(self, app, canvas):  # used for inheritance
        drawBeam(app, canvas, self.x1, self.y1, self.x2, self.y2)

class VerticalBeam():  # moves vertically
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.type = 'vertical'
        self.width = app.cellSize
        self.centerY = app.barY+((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2
        self.timePosition = 0
        [self.timeStarted, self.snapShot] = [0, 0]
        [self.frozen, self.timePaused] = [False, 0]
        if app.timeDilation == 3: self.dilate(app)

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+self.xScale+self.width < 0

    def freeze(self, state):  # variables for app.paused
        if state: self.timeFrozen = time.time()
        else: self.timePaused += (time.time()-self.timeFrozen)
        self.frozen = state

    def dilate(self, app):  # variables for time/speed changes
        self.timeStarted = time.time()-app.timeInitial
        self.snapShot = self.timePosition

    def interacts(self, app, player):
        if self.frozen: timePosition = (self.timeFrozen-self.timePaused)-\
                                       app.timeInitial
        else: timePosition = (time.time()-self.timePaused)-app.timeInitial
        self.timePosition = ((timePosition-self.timeStarted)/app.timeDilation)+\
                       self.snapShot
        yPosition = self.yScale*math.cos(2*math.pi*(self.timePosition%1))
        pa = [self.centerX-self.xScale, self.centerY+yPosition]
        pb = [self.centerX+self.xScale, self.centerY+yPosition]
        return minDistance(pa, pb, [player.x, player.y]) <= (player.sizeX/2)

    def draw(self, app, canvas):
        [x1, x2] = [self.centerX-self.xScale, self.centerX+self.xScale]
        if self.frozen: timePosition = (self.timeFrozen-self.timePaused)-\
                                       app.timeInitial
        else: timePosition = (time.time()-self.timePaused)-app.timeInitial
        timePosition = ((timePosition-self.timeStarted)/app.timeDilation)+\
                            self.snapShot
        yPosition = self.yScale*math.cos(2*math.pi*(timePosition%1))
        y = self.centerY+yPosition
        drawBeam(app, canvas, x1, y, x2, y)

class HorizontalBeam():  # moves horizontally
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.type = 'horizontal'
        self.width = app.cellSize
        self.centerY = app.barY+((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2
        self.timePosition = 0
        [self.timeStarted, self.snapShot] = [0, 0]
        [self.frozen, self.timePaused] = [False, 0]
        if app.timeDilation == 3: self.dilate(app)

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+(2*self.xScale)+self.width < 0

    def freeze(self, state):  # variables for app.paused
        if state: self.timeFrozen = time.time()
        else: self.timePaused += (time.time()-self.timeFrozen)
        self.frozen = state

    def dilate(self, app):  # variables for time/speed changes
        self.timeStarted = time.time()-app.timeInitial
        self.snapShot = self.timePosition

    def interacts(self, app, player):
        if self.frozen: timePosition = (self.timeFrozen-self.timePaused)-\
                                       app.timeInitial
        else: timePosition = (time.time()-self.timePaused)-app.timeInitial
        self.timePosition = ((timePosition-self.timeStarted)/app.timeDilation)+\
                            self.snapShot
        xPosition = self.xScale*math.cos(2*math.pi*(self.timePosition%1))
        pa = [self.centerX+xPosition, self.centerY-self.yScale]
        pb = [self.centerX+xPosition, self.centerY+self.yScale]
        return minDistance(pa, pb, [player.x, player.y]) <= (player.sizeX/2)

    def draw(self, app, canvas):
        [y1, y2] = [self.centerY-self.yScale, self.centerY+self.yScale]
        if self.frozen: timePosition = (self.timeFrozen-self.timePaused)-\
                                        app.timeInitial
        else: timePosition = (time.time()-self.timePaused)-app.timeInitial
        timePosition = ((timePosition-self.timeStarted)/app.timeDilation)+\
                       self.snapShot
        xPosition = self.xScale*math.cos(2*math.pi*(timePosition%1))
        x = self.centerX+xPosition
        drawBeam(app, canvas, x, y1, x, y2)

class RotatingBeam():  # rotate left or right
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.type = 'rotating'
        self.width = app.cellSize
        self.centerY = app.barY+((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2
        [self.timeStarted, self.snapShot] = [0, 0]
        self.timePosition = 0
        [self.frozen, self.timePaused] = [False, 0]
        if app.timeDilation == 3: self.dilate(app)

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+(2*self.xScale)+self.width < 0

    def freeze(self, state):  # variables for app.paused
        if state: self.timeFrozen = time.time()
        else: self.timePaused += (time.time()-self.timeFrozen)
        self.frozen = state

    def dilate(self, app):  # variables for time/speed changes
        self.timeStarted = time.time()-app.timeInitial
        self.snapShot = self.timePosition

    def getAngle(self, app, view):  # gets current angle using trig
        if self.frozen: timePosition = (self.timeFrozen-self.timePaused)-\
                                        app.timeInitial
        else: timePosition = (time.time()-self.timePaused)-app.timeInitial
        timePosition = ((timePosition-self.timeStarted)/app.timeDilation)+\
                       self.snapShot
        if not view: self.timePosition = timePosition
        return math.pi+(math.pi*(math.cos(((2*(timePosition%1))*math.pi)/2)))

    def interacts(self, app, player): # animation curve below
        angle = self.getAngle(app, False)
        [dy, dx] = [self.yScale*math.sin(angle),
                    self.yScale*math.cos(angle)]
        return minDistance([(self.centerX-dx), (self.centerY-dy)],
            [(self.centerX+dx), (self.centerY+dy)], [player.x, player.y]) <= \
               (player.sizeX/2)

    def draw(self, app, canvas):  # animation curve below
        angle = self.getAngle(app, True)
        if almostEqual(angle, 2*math.pi): angle = 0
        [dy, dx] = [self.yScale*math.sin(angle), self.yScale*math.cos(angle)]
        [x1, y1, x2, y2] = [self.centerX-dx, self.centerY-dy,
                            self.centerX+dx, self.centerY+dy]
        drawBeam(app, canvas, x1, y1, x2, y2)

class Missile():
    def __init__(self, app, y):
        self.fireStart = time.time()  # time since ignition
        self.x = app.width+(app.missile.size[0]/2)  # in next chunk
        self.y = y

    def move(self, app):
        if (int((time.time()-self.fireStart)*10))/10 > 0.5:  # 1 second curve
            self.fireStart = time.time()
        self.x -= app.missileMultiplier*app.speed  # slightly faster

    def interacts(self, app, x, y):  # hit box consists of two meeting lines
        [ax1, bx1] = [self.x-(app.missile.size[0]/2),
                      self.x-(app.missile.size[0]/2)]
        [ax2, bx2] = [self.x+(app.missile.size[0]/3),
                      self.x+(app.missile.size[0]/3)]
        [ay1, by1] = [self.y, self.y]
        ay2 = self.y-(app.missile.size[1]/3)
        by2 = self.y+(app.missile.size[1]/3)
        return (minDistance([ax1, ay1], [ax2, ay2], [x, y]) <=
                (app.player.sizeX/2)) or (minDistance([bx1, by1], [bx2, by2],
                [x, y]) <= (app.player.sizeX/2))

    def draw(self, app, canvas):
        shakeY = random.choice([-2, -1, 0, 1, 2])  # shakes up and down
        canvas.create_image(self.x, self.y+shakeY,
                            image=ImageTk.PhotoImage(app.missile))
        self.drawFire(app, canvas, shakeY)
        if app.timeDilation == 3: canvas.create_image(self.x, self.y,
                                    image=ImageTk.PhotoImage(app.clock))

    def drawFire(self, app, canvas, shakeY):
        key = (int((time.time()-self.fireStart)*10))/10  # 1 second curve
        if key > 0.5: key = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])
        image = ImageTk.PhotoImage(app.missileFire[key])
        x = self.x+(app.missile.size[0]/2)+(app.missileFire[key].size[0]/2)
        canvas.create_image(x, self.y+shakeY, image=image)

class Exclamation():  # exclamation point that appears before and makes missiles
    def __init__(self, app, y, waitTime):
        self.y = y
        self.waitTime = waitTime  # depends on difficulty
        self.startMissileWait = time.time()
        self.frozen = False

    def freeze(self, state):
        if state: self.timePaused = time.time()
        else: self.waitTime += (time.time()-self.timePaused)
        self.frozen = state

    def createMissile(self, app):
        if (not self.frozen) and (time.time()-self.startMissileWait >=
                                  self.waitTime):
            app.missiles += [Missile(app, self.y)]
            return True
        return False

    def draw(self, app, canvas):
        x = app.width-(2*app.cellSize)
        fontSize = 50*app.scale
        font = 'Times', str(int(fontSize)), 'bold'
        canvas.create_text(x, self.y, fill='red', text='!', anchor='center',
                           font=font)

class Booster():  # rocket fuel power up
    def __init__(self, app, x, y):
        [self.x, self.y] = [app.width+x, y]
        [self.active, self.frozen] = [False, False]  # waiting on the board
        self.priorSpeed = app.speed
        self.sprite = app.gas
        self.timeLength = 10

    def interacts(self, app, x, y):
        if math.sqrt(((self.x-x)**2)+((self.y-y)**2)) <= (app.player.sizeX):
            self.activate(app)

    def freeze(self, state):  # variables for app.paused
        if state: self.timePaused = time.time()
        else: self.timeLength += (time.time()-self.timePaused)
        self.frozen = state

    def activate(self, app):
        [self.active, app.powerUp, self.called] = [True, True, False]
        [self.x, self.y] = [app.width/5, app.barY/2]
        self.timeInitial = time.time()
        [app.invincible, app.missiles, app.lazyGeneration] = [True, [], True]
        [app.player.freezeFactor, self.finishDrops] = [2, app.dDrops]

    def manage(self, app):  # hides and shows Cohon sprites
        if self.active:
            timeSinceStart = time.time()-self.timeInitial
            inflationScale = math.sin(math.pi*timeSinceStart/self.timeLength)
            app.speed = self.priorSpeed+(inflationScale*self.priorSpeed*10)
            if 8 <= (self.timeLength-(time.time()-self.timeInitial)) <= 10:
                app.dropY += 5*app.scale
            elif 2 < (self.timeLength-(time.time()-self.timeInitial)) < 8:
                app.dDrops = False
            elif 0 <= (self.timeLength-(time.time()-self.timeInitial)) <= 2:
                if not self.called:
                    for i in range((app.width//app.dropSize[0])+2):
                        app.drops += [BackDrop(app, i, False, 1)]
                    self.called = True
                if self.finishDrops: app.dDrops = True
                app.dropY -= 5*app.scale
            elif self.timeLength-(time.time()-self.timeInitial) < 0:
                app.dropY = 0
            for drop in app.drops:
                drop.y = app.height-(app.dropSize[1]/2)+app.dropY
        return managePowerUp(self, app)

    def deactivate(self, app):
        [app.invincible, app.powerUp, app.dropY] = [False, False, 0]
        app.lazyGeneration = False
        app.speed = self.priorSpeed
        app.player.freezeFactor = 1

    def draw(self, app, canvas):
        drawPowerUp(self, app, canvas)

class Invincibility():  # heart power up
    def __init__(self, app, x, y):
        [self.x, self.y] = [app.width+x, y]
        [self.active, self.frozen] = [False, False]  # waiting on the board
        self.priorSpeed = app.speed
        self.sprite = app.heart
        self.timeLength = 10  # 10 seconds long

    def interacts(self, app, x, y):
        if math.sqrt(((self.x-x)**2)+((self.y-y)**2)) <= (app.player.sizeX):
            self.activate(app)

    def freeze(self, state):  # variables for app.paused
        if state: self.timePaused = time.time()
        else: self.timeLength += (time.time()-self.timePaused)
        self.frozen = state

    def activate(self, app):
        [self.active, app.powerUp] = [True, True]
        [self.x, self.y] = [app.width/5, app.barY/2]
        self.timeInitial = time.time()
        [app.invincible, app.missiles] = [True, []]

    def manage(self, app):
        if self.active:
            timeSinceStart = time.time()-self.timeInitial
            inflationScale = math.sin(math.pi*timeSinceStart/self.timeLength)
            app.speed = self.priorSpeed+((inflationScale*app.speed*3)/5)
        return managePowerUp(self, app)

    def deactivate(self, app):
        [app.invincible, app.powerUp] = [False, False]
        app.speed = self.priorSpeed  # speed reset

    def draw(self, app, canvas):
        drawPowerUp(self, app, canvas)

class TimeSlower():  # power up that slows down time
    def __init__(self, app, x, y):
        [self.x, self.y] = [app.width+x, y]
        [self.active, self.frozen] = [False, False]
        self.sprite = app.clockCircle
        self.timeLength = 15  # 15 seconds long

    def interacts(self, app, x, y):
        if math.sqrt(((self.x-x)**2)+((self.y-y)**2)) <= (app.player.sizeX):
            self.activate(app)

    def freeze(self, state):
        if state: self.timePaused = time.time()
        else: self.timeLength += (time.time()-self.timePaused)
        self.frozen = state

    def activate(self, app):
        [self.active, app.powerUp] = [True, True]
        [self.x, self.y] = [app.width/5, app.barY/2]
        self.timeInitial = time.time()
        app.timeDilation = 3  # three times as slow
        for beam in app.beams:
            if beam.type != 'static': beam.dilate(app)
        app.speed = app.speed/app.timeDilation

    def manage(self, app):
        return managePowerUp(self, app)

    def deactivate(self, app):
        app.powerUp = False
        app.speed = app.speed*app.timeDilation  # resets speed
        app.timeDilation = 1
        for beam in app.beams:
            if beam.type != 'static': beam.dilate(app)
    def draw(self, app, canvas):
        drawPowerUp(self, app, canvas)

class Cloud():  # background objects that do not influence gameplay
    def __init__(self, app, id):
        self.id = id
        [self.sizeX, self.sizeY] = [26*app.scale, 11*app.scale]
        self.speedRange = [1, 1.1]
        self.sizeRange = [1, 2]
        self.coordsRange = app.barY+(app.trueHeight//3)
        self.reDefine(app, random.randint(0, app.width))

    def reDefine(self, app, x):  # recreates new cloud at right end of screen
        self.sprite = app.loadImage('sprites/cloud0.png')
        if self.id % 2 == 0:
            self.sprite = self.sprite.transpose(Image.FLIP_LEFT_RIGHT)
        self.size = app.scale*random.choice(self.sizeRange)
        self.speed = app.speed*app.scale*random.choice(self.speedRange)
        self.x = x
        self.y = random.randint(app.barY+int(self.sizeY*self.size),
                                self.coordsRange)
        self.sprite = app.scaleImage(self.sprite, self.size)

    def move(self, app):
        if self.x+(self.sizeX*self.size) < 0: self.reDefine(app, app.width)
        if app.start: self.x -= abs(self.speed/app.cloudMultiplier)
        else: self.x -= abs(self.speed/(app.cloudMultiplier*8))

    def draw(self, canvas):
        [x1, y1] = [self.x+(self.size*(self.sizeX/2)),
                    self.y+(self.size*(self.sizeY/2))]
        canvas.create_image(x1, y1, image=ImageTk.PhotoImage(self.sprite))

class Chunk():  # 2D list includes locations of coins/obstacles
    def __init__(self, app, oldChunk, x):
        # newChunk becomes oldChunk
        if oldChunk: [self.literal, self.x] = [copy.deepcopy(oldChunk), x]
        else:  # brand new chunk create from scratch
            self.literal = chunkGeneration.generationManager(app, x)
            self.x = x

class JetpackScotty(App):  # main app class
    def appStarted(self):  # variables not reset by restartApp
        [self.rows, self.cols, self.points] = [20, 40, 0]
        [self.diffInc, self.speedDifference] = [5, 3]
        [self.pathfinderStall, self.usePowerUps] = [0.5, True]
        [self.cloudNumer, self.longestRun, self.currentRun] = [3, 0, 0]
        [self.barPortion, self.standardizedWidth] = [9, 800]
        [self.standardizedHeight, self.missileMultiplier] = [400, 2.5]
        self.barY = (self.height//self.barPortion)
        self.buttonSizes = (2*self.barY)//3
        self.scale = self.width/self.standardizedWidth
        self.buttonSpacing = (self.barY-self.buttonSizes)//2
        if self.width <= 400: self.buttonSizes = self.barY
        self.trueHeight = self.height-self.barY
        self.scaleY = self.trueHeight/self.standardizedHeight
        [self.timerDelay, self.coinSize, self.coinSpacing, self.cellSize] = \
            [1, 16*self.scale, 4*self.scale, self.width/self.cols]
        [self.dropMultiplier, self.cloudMultiplier] = [1.25, 2]
        self.restartApp()

    def loadIndividualSprites(self):  # for distinct sprites
        self.scottyImages = {-1: self.loadImage('sprites/airborne.png')}
        self.scottyImages[-2] = \
            self.scottyImages[-1].transpose(Image.ROTATE_270)
        [self.coinSequence, self.igniteImages, self.buttons, self.missileFire,
         self.rightFire] = [{}, {}, {}, {}, {}]
        self.buttons['pause'] = self.loadImage('sprites/pause.png')
        self.clockCircle = self.scaleImage(
            self.loadImage('sprites/clockCircle.png'), self.scale)
        self.clock = self.scaleImage(self.loadImage('sprites/clock.png'),
                                     self.scale)
        self.heart = self.scaleImage(self.loadImage('sprites/heart.png'),
                                     self.scale)
        self.miniHeart = self.scaleImage(
            self.loadImage('sprites/miniHeart.png'), self.scale)
        self.buttons['play'] = self.loadImage('sprites/play.png')
        self.buttons['exit'] = self.loadImage('sprites/exit.png')
        self.buttons['reset'] = self.loadImage('sprites/reset.png')
        self.buttons['settings'] = self.loadImage('sprites/settings.png')
        for button in self.buttons: self.buttons[button] = \
            self.scaleImage(self.buttons[button], self.scale)
        self.missile = self.loadImage('sprites/missile.png')
        self.missile = self.scaleImage(self.missile, 1.5*self.scale)
        self.gas = self.scaleImage(self.loadImage('sprites/gas.png'),
                                   self.scale)

    def loadSprites(self):  # for sets of similar sprites
        self.loadIndividualSprites()
        self.coinCoordsRange = [(self.width//(self.coinSize+self.coinSpacing)),
            (self.trueHeight//(self.coinSize+self.coinSpacing))]
        for i in range(4): self.coinSequence[i] = self.scaleImage(
            self.loadImage('sprites/coin'+str(i)+'.png'), self.scale)
        for i in range(2, -1, -1):
            image = self.scaleImage(self.loadImage('sprites/coin'+str(i)+
                                                   '.png'), self.scale)
            self.coinSequence[6-i] = image.transpose(Image.FLIP_LEFT_RIGHT)
        for i in range(3): self.scottyImages[i] = \
            self.loadImage('sprites/scotty'+str(i)+'.png')
        for imageKey in self.scottyImages: self.scottyImages[imageKey] = \
                self.scaleImage(self.scottyImages[imageKey], self.scale)
        dropImage = self.scaleImage(self.loadImage('sprites/cohon0.tiff'),
                                    self.scale*2)
        self.dropSize = [dropImage.size[0], dropImage.size[1]]
        self.dropImages = {0: dropImage,
            1: dropImage.transpose(Image.FLIP_LEFT_RIGHT)}
        self.dropImages[2] = self.scaleImage(
            self.loadImage('sprites/cohon1.png'), self.scale*2)
        for i in range(17): self.igniteImages[i/10] = self.scaleImage(
            self.loadImage('sprites/ignite'+str(i)+'.png'), self.scale)
        self.igniteImages[1.7] = self.igniteImages[1.5].\
            transpose(Image.FLIP_LEFT_RIGHT)
        self.igniteImages[1.8] = self.igniteImages[1.6].\
            transpose(Image.FLIP_LEFT_RIGHT)
        for i in range(3): self.missileFire[i/10] = self.scaleImage(
            self.loadImage('sprites/blue'+str(i)+'.png'), 1.5*self.scale)
        for i in range(3, 6): self.missileFire[i/10] = self.missileFire[
            (i-3)/10].transpose(Image.FLIP_TOP_BOTTOM)
        for i in range(6): self.rightFire[i/10] = self.missileFire[i/10].\
            transpose(Image.FLIP_LEFT_RIGHT)
        for button in self.buttons:
            scale = self.buttonSizes/self.buttons[button].size[0]
            self.buttons[button] = self.scaleImage(self.buttons[button], scale)

    def restartApp(self):  # variables reset on death
        chunkGeneration.resetLongs(self)  # player data is reset
        chunkGeneration.resetStandards(self)
        chunkGeneration.resetFasts(self)
        self.difficulty = 'medium'
        [self.dDrops, self.dCoins, self.lazyGeneration] = [True, True, False]
        if self.currentRun > self.longestRun: self.longestRun = self.currentRun
        [self.currentRun, self.lazyGeneration, self.deaths] = [0, False, 0]
        [self.debug, self.paused, self.settingsOpen] = [False, False, True]
        [self.kill, self.firstChunk, self.powerUp] = [False, True, False]
        self.loadSprites()
        [self.movement, self.difficultyBase] = [10*self.scale, 0]
        [self.coinStart, self.gameOver, self.dropY] = [False, False, 0]
        [self.downInitial, self.upInitial, self.timeInitial, self.pausedTime] =\
            [time.time()-1, time.time()-1, time.time()+1, 0]
        [self.timeDilation, self.invincible, self.start] = [1, False, False]
        self.changeSpeedGraphics(draw=self.dDrops)
        self.player = Scotty(self, self.scottyImages, self.igniteImages)
        [self.coins, self.clouds, self.beams, self.drops, self.missiles,
         self.warnings, self.powerUps] = [[], [], [], [], [], [], []]
        self.specialCoin = Coin(self, False, False, False, True)
        self.currentChunk = Chunk(self, False, self.width)
        [self.firstChunk, self.explosionX, self.highlight] = \
            [False, False, False]
        self.newChunk = Chunk(self, False, 2*self.width)
        for i in range(self.cloudNumer): self.clouds += [Cloud(self, i)]
        self.dropSetup()

    def getQuitMessage(self):  # alters default quit message
        return '\n*** Closing Jetpack Scotty. I hope you enjoyed! ***\n'

    def dropSetup(self):  # makes new drops fro restartApp
        self.drops += [BackDrop(self, False, False, 2)]
        for i in range((self.width//self.dropSize[0])+2):
            self.drops += [BackDrop(self, i, False, 1)]

    def checkCoinInteraction(self):  # calls .interacts methods for coins
        coinSpace = min([self.player.sizeX, self.player.sizeY])+self.coinSize/3
        newCoins = []
        for coin in self.coins:
            if coin.interacts(self.player.x, self.player.y, coinSpace):
                self.points += 1
                self.coinStart = time.time()
            else: newCoins += [coin]
        self.coins = newCoins

    def getCachedPhotoImage(self, image):  # helpful for many sprites
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def explosionSetUp(self, missile):  # creates missile explosion
        [self.explosionX, self.explosionY] = [missile.x, missile.y]
        self.maxRadius = [self.trueHeight, self.trueHeight/2, self.trueHeight/3]
        self.TOD = time.time()

    def killAll(self):  # puts game in gameOver state but does not reset
        self.gameOver = True
        pauseGame(self)
        self.deaths += 1
        [self.killXSize, self.killYSize] = [self.width/4, self.trueHeight/4]
        [self.miniXSize, self.miniYSize] = [(9*self.killXSize)/10,
                                            (9*self.killYSize)/10]
        [self.killX, self.killY] = [self.width/2, self.height+self.killYSize]
        [self.respawnSizeX, self.respawnSizeY] = [self.killXSize/3,
                                                  self.killYSize/3]
        if self.powerUp:
            newPowerUps = []
            for power in self.powerUps:
                if power.active: power.deactivate(self)
                elif not power.manage(self): newPowerUps += [power]
            self.powerUps = newPowerUps

    def respawn(self):  # gives invincibility and revives player
        self.gameOver = False
        pauseGame(self)
        self.points -= 100
        if self.usePowerUps: self.powerUps += [Invincibility(self,
            self.player.x-self.width, self.player.y)]  # temp invincibility
        self.timeDilation = 1  # counters increased speed of invincibility
        [self.explosionX, self.explosionY] = [False, False]

    def manageObstacles(self):  # obstacle objects only
        [newBeams, kill, newWarnings, newMissiles] = [[], False, [], []]
        if self.newChunk.x <= 0:
            self.currentChunk = Chunk(self, self.newChunk.literal,
                                      self.newChunk.x)
            self.newChunk = Chunk(self, False, self.width)
        for beam in self.beams:
            if (not self.invincible) and (beam.interacts(self, self.player)):
                kill = True
                q = chunkGeneration.getQuadrantFromY(self, self.player.y)
                self.beamDeathQuadrants[q] += 1
                self.beamDeathTypes[beam.type] += 1
            if not beam.outOfBounds(): newBeams += [beam]
        for warning in self.warnings:
            if not warning.createMissile(self): newWarnings += [warning]
        for missile in self.missiles:
            if (not self.invincible) and (missile.interacts(self, self.player.x,
                self.player.y)):
                self.explosionSetUp(missile)
                q = chunkGeneration.getQuadrantFromY(self, missile.y)
                self.missileDeaths[q] += 1
                kill = True
            elif missile.x+(self.missile.size[0]/2)+self.missileFire[0].size[0]\
                    > 0: newMissiles += [missile]
            else:
                q = chunkGeneration.getQuadrantFromY(self, missile.y)
                self.missileAvoids[q] += 1
        if kill: self.killAll()
        [self.beams, self.warnings, self.missiles] = \
            [newBeams, newWarnings, newMissiles]

    def manageAll(self):  # deletes and adds objects based on locations
        if time.time()-self.balance >= 150: chunkGeneration.resetStandards(self)
        if time.time()-self.beamBalance >= 50: chunkGeneration.resetFasts(self)
        if time.time()-self.longBalance >= 500: chunkGeneration.resetLongs(self)
        [newCoins, newPowerUps] = [[], []]
        for coin in self.coins:
            if coin.x > (-self.coinSize): newCoins += [coin]
        for power in self.powerUps:
            if self.powerUp:
                if power.active and (not power.manage(self)):
                    newPowerUps += [power]
            elif not power.manage(self):
                newPowerUps += [power]
        if self.drops[0].type == 2:
            if self.drops[0].x+(self.dropImages[2].size[0]/2) < 0:
                self.drops = self.drops[1:]
                recentX = self.drops[-1].x+self.dropSize[0]
                self.drops += [BackDrop(self, False, recentX, 1)]
        elif self.drops[0].x+(self.dropSize[0]/2) < 0:
            self.drops = self.drops[1:]
            recentX = self.drops[-1].x+self.dropSize[0]
            self.drops += [BackDrop(self, False, recentX, 1)]
        [self.coins, self.powerUps] = [newCoins, newPowerUps]
        self.manageObstacles()
        self.checkCoinInteraction()

    def moveAll(self):  # moves all objects at various speeds
        self.player.manage()
        self.currentRun += self.speed
        self.newChunk.x -= self.speed
        self.currentChunk.x -= self.speed
        for cloud in self.clouds: cloud.move(self)
        for drop in self.drops: drop.move(self)
        for coin in self.coins: coin.x -= self.speed
        for beam in self.beams: beam.move(self)
        for missile in self.missiles: missile.move(self)
        self.manageAll()

    def changeSpeedGraphics(self, draw=None):  # alters speed and/or graphics
        if draw == True: self.dDrops = True
        elif draw == False: self.dDrops = False
        difficulty = chunkGeneration.getDifficulty(self)+self.difficultyBase
        if draw == 'pass': return difficulty
        if self.dDrops: self.speed = self.speedDifference*self.scale*(2+
                            (difficulty/10))/self.timeDilation
        else: self.speed = self.scale*(2+(difficulty/10))/self.timeDilation
        return difficulty

    def getDifficultyBoxes(self):  # rectangles for difficulty selection
        [boxes, midX] = [[], (self.width*7)/8]
        [xSpan, ySpan] = [self.width/9, (self.trueHeight/25)]
        for i in range(2, 5):
            y = self.barY+((i*self.trueHeight)/10)
            boxes += [[midX-xSpan, y-ySpan, midX+xSpan, y+ySpan]]
        return boxes+[['Easy', 'Medium', 'Hard'], ['green', 'yellow', 'red']]

    # checks if settings are clicked or hovered over
    def clickSettings(self, eventX, eventY, click):
        boxes = self.getDifficultyBoxes()
        self.highlight = False
        if not (boxes[0][0] <= eventX <= boxes[0][2]): return None
        for i in range(3):
            box = boxes[i]
            if box[1] <= eventY <= box[3]:
                if not click: self.highlight = box
                else:
                    self.difficulty = boxes[3][i].lower()
                    if not self.start:
                        [self.start, self.settingsOpen] = [True, False]
                        self.changeSpeedGraphics()

    def mouseMoved(self, event):
        if self.settingsOpen: self.clickSettings(event.x, event.y, False)
        else: self.hilight = False

    def timerFired(self):
        if self.difficulty == 'hard': self.changeSpeedGraphics(draw=False)
        if self.start:
            if self.gameOver and (self.killY > (self.trueHeight/2)+self.barY):
                self.killY -= 10*self.scale  # moves game over screen
            self.specialCoin.changeTimeState(self)
            if not self.paused: self.moveAll()
            if self.player.up:
                if self.dDrops: self.player.move(self, ((3*self.speedDifference)
                    /4)*(-4*self.scale*(time.time()-self.upInitial+1)**(1/2)))
                else: self.player.move(self, (-4*self.scale*(time.time()-
                                        self.upInitial+1)**(1/2)))
            elif (not self.paused) or self.gameOver:
                if self.dDrops: self.player.move(self, ((3*self.speedDifference)
                 /2)*(self.scale*10*math.log(time.time()-self.downInitial+1)))
                else: self.player.move(self, (self.scale*10*math.log(time.time()
                                        -self.downInitial+1)))
        else:  # still move on main menu
            for cloud in self.clouds: cloud.move(self)

    def mousePressed(self, event):
        if self.settingsOpen: self.clickSettings(event.x, event.y, True)
        if (self.points >= 100) and (self.gameOver):  # check for respawn click
            box = [self.killX-self.respawnSizeX, self.killY-self.respawnSizeY,
                    self.killX+self.respawnSizeX, self.killY+self.respawnSizeY]
            if (box[0] <= event.x <= box[2]) and ((self.height/10)+box[1] <=
                event.y <= (self.height/10)+box[3]): self.respawn()
        if ((self.barY-self.buttonSizes)/2) <= event.y <= self.barY-\
                ((self.barY-self.buttonSizes)/2):  # check for button click
            if (self.width-self.buttonSpacing-self.buttonSizes <= event.x <=
                self.width-self.buttonSpacing) and (not self.gameOver):
                pauseGame(self)
                if self.settingsOpen: self.settingsOpen = False
            if self.width-(2*(self.buttonSpacing+self.buttonSizes)) <= event.x \
                    <= self.width-(2*self.buttonSpacing)-self.buttonSizes:
                self.restartApp()
            if (self.width-(3*(self.buttonSpacing+self.buttonSizes)) <= event.x
                    <= self.width-(3*self.buttonSpacing)-(2*self.buttonSizes))\
                    and (not self.gameOver):
                self.settingsOpen = not self.settingsOpen
                if not self.paused: pauseGame(self)
        elif (not self.player.up) and (not self.paused) and self.start:
            [self.player.airborne, self.player.up] = [True, True]
            [self.player.sizeX, self.player.sizeY] = [35*self.scale,
                                                      46*self.scale]
            self.upInitial = time.time()+0

    def mouseReleased(self, event):
        if self.player.up:  # rising
            self.player.up = False
            self.downInitial = time.time()+0

    def keyPressed(self, event):
        if event.key.lower() == 'd': self.debug = not self.debug
        elif event.key.lower() == 'right':
            self.difficultyBase += self.diffInc
            if not self.powerUp: self.changeSpeedGraphics()
        elif (event.key.lower() == 'left') and (self.difficultyBase-
            self.diffInc > 0):
            self.difficultyBase -= self.diffInc
            if not self.powerUp: self.changeSpeedGraphics()
        elif event.key.lower() == 'i': self.usePowerUps = not self.usePowerUps
        elif event.key.lower() == 'p': testCode.printer(self)
        elif event.key.lower() == 'c': self.points += 1000
        elif event.key.lower() == 'm': chunkGeneration.missileGenerator(self,
                50, True)  # instantly generates a missile
        elif event.key.lower() == 'g':  # changes graphics
            if self.dDrops: self.changeSpeedGraphics(draw=False)
            else: self.changeSpeedGraphics(draw=True)
        elif event.key.lower() == 't': testCode.printData(self)

    def sizeChanged(self):  # certain variables must be reset from appStarted
        self.scale = self.width/self.standardizedWidth
        self.standardizedHeight = 400
        self.barY = (self.height//self.barPortion)
        self.buttonSizes = (2*self.barY)//3
        self.buttonSpacing = (self.barY-self.buttonSizes)//2
        if self.width <= 400: self.buttonSizes = self.barY
        self.trueHeight = self.height-self.barY
        self.scaleY = self.trueHeight/self.standardizedHeight
        self.cellSize = self.width/self.cols
        [self.coinSize, self.coinSpacing] = [16*self.scale, 4*self.scale]
        self.restartApp()

    def redrawAll(self, canvas):
        self.drawSky(canvas)
        if self.dDrops:  # draws Cohon
            for drop in self.drops: drop.draw(self, canvas)
        if self.debug:  # hitboxes and grid drawn
            testCode.drawBorders(self.currentChunk.x, self, canvas, 'red')
            testCode.drawBorders(self.newChunk.x, self, canvas, 'blue')
        self.player.draw(self, canvas, self.debug)
        self.player.drawFire(self, canvas)
        for coin in self.coins:
            if coin.x-self.cellSize <= self.width: coin.draw(self, canvas,
                self.debug, self.coinSequence, self.coinSize)
        if self.start:
            for beam in self.beams: beam.draw(self, canvas)
            for exclamation in self.warnings: exclamation.draw(self, canvas)
            for missile in self.missiles: missile.draw(self, canvas)
            for powerUp in self.powerUps: powerUp.draw(self, canvas)
            if self.gameOver:
                if self.explosionX: self.drawExplosion(canvas)
                self.drawGameOver(canvas)
        else: self.drawStart(canvas)
        self.drawStatusBar(canvas)

    def drawStart(self, canvas):  # draws start screen
        y = self.barY+(self.trueHeight/4)
        canvas.create_rectangle((self.width/3)-(self.width/4),
            y-(self.trueHeight/6), (self.width/3)+(self.width/4),
                            y+(self.trueHeight/6), fill='grey')
        canvas.create_rectangle((self.width/3)-((self.width*2)/9),
            y-(self.trueHeight/7), (self.width/3)+((self.width*2)/9),
                            y+(self.trueHeight/7), fill='darkgrey')
        fontSize = int(45*self.scale)  # large title text
        font = 'Arial', str(fontSize), 'bold'
        canvas.create_text(self.width/3, y, fill='maroon', anchor='center',
            text='Jetpack Scotty', font=font, activefill='black')

    def drawExplosion(self, canvas):
        totalTime = 0.1
        if time.time()-self.TOD <= totalTime:
            colors = ['white', 'orange', 'red']
            for i in range(3):  # three rings
                radius = (self.maxRadius[i]*(time.time()-self.TOD))/totalTime
                canvas.create_oval(self.explosionX-radius,
                    self.explosionY-radius, self.explosionX+radius,
                    self.explosionY+radius, fill=colors[i], width=0)

    def drawGameOver(self, canvas):  # game over screen
        box1 = [self.killX-self.killXSize, self.killY-self.killYSize,
                self.killX+self.killXSize, self.killY+self.killYSize]
        box2 = [self.killX-self.miniXSize, self.killY-self.miniYSize,
                self.killX+self.miniXSize, self.killY+self.miniYSize]
        box3 = [self.killX-self.respawnSizeX, self.killY-self.respawnSizeY,
                self.killX+self.respawnSizeX, self.killY+self.respawnSizeY]
        fontSize = 50*(self.width//self.standardizedWidth)
        font = 'Times', str(fontSize), 'bold'
        canvas.create_rectangle(box1[0], box1[1], box1[2], box1[3],
                                fill='darkgrey')
        canvas.create_rectangle(box2[0], box2[1], box2[2], box2[3], fill='grey')
        canvas.create_text(self.killX, self.killY-(self.killYSize/5),
            fill='red', text='Game Over!', anchor='center', font=font)
        if self.points < 100: box = 'red'  # cannot respawn
        else: box = 'green'  # can respawn
        canvas.create_rectangle(box3[0], (self.height/10)+box3[1], box3[2],
                            (self.height/10)+box3[3], fill=box)
        fontSize = 24*(self.width//self.standardizedWidth)
        font = 'Times', str(fontSize), 'bold'
        canvas.create_text(self.killX, self.killY+(self.height/15),
                fill='black', text='Respawn?', font=font)
        canvas.create_image(self.killX-(20*self.scale), self.killY+(
            self.height/8), image=ImageTk.PhotoImage(self.coinSequence[0]))
        canvas.create_text(self.killX+(15*self.scale), self.killY+(
            self.height/8), fill='black', text='100', font=font)

    def drawStatusBar(self, canvas):  # top bar with statuses and buttons
        self.drawUpperCoin(canvas)
        self.drawButtons(canvas)
        if self.start: self.drawCurrentRun(canvas)
        if self.settingsOpen: self.drawSettings(canvas)

    def drawUpperCoin(self, canvas):  # coin number in upper left
        xPosition = (3*self.buttonSpacing)+self.buttonSizes
        font = 'Times', str(int(24*self.scale)), 'bold italic'
        canvas.create_text(xPosition, self.barY/2, activefill='gold',
                    fill='black', text=self.points, anchor='w', font=font)
        self.specialCoin.draw(self, canvas, self.debug, self.coinSequence,
                              self.coinSize)

    def drawCurrentRun(self, canvas):  # current run/high score with distance
        xPosition = self.width/2
        fontSize = int(24*self.scale)
        font = 'Times', str(fontSize), 'bold'
        if self.currentRun >= self.longestRun:
            text = 'High Score! '+str(int(self.currentRun//100))+'m'
            colors = ['darkgrey', 'gold']  # meters obtained by dividing by 100
        else:
            text = 'Current Run '+str(int(self.currentRun//100))+'m'
            colors = ['lightgrey', 'black']
        canvas.create_rectangle(xPosition-4*self.buttonSizes,
            self.buttonSpacing, xPosition+4*self.buttonSizes,
            self.barY-self.buttonSpacing, fill=colors[0])
        canvas.create_text(xPosition, self.barY/2, activefill='gold',
                    fill=colors[1], text=text, anchor='center', font=font)

    def drawButtons(self, canvas):  # three buttons with changing sprites
        y = self.barY//2
        pausedX = self.width-self.buttonSpacing-(self.buttonSizes//2)
        restartX = self.width-(2*self.buttonSpacing)-((3*self.buttonSizes)//2)
        settingsX = self.width-(3*self.buttonSpacing)-((5*self.buttonSizes)//2)
        if self.paused and (not self.gameOver):  # draw pause/play
            image = ImageTk.PhotoImage(self.buttons['play'])
        else: image = ImageTk.PhotoImage(self.buttons['pause'])
        if (not self.gameOver) and self.start:
            canvas.create_image(pausedX, y, image=image)
        if self.settingsOpen: image = ImageTk.PhotoImage(self.buttons['exit'])
        else: image = ImageTk.PhotoImage(self.buttons['settings'])
        if (not self.gameOver) and self.start:
            canvas.create_image(settingsX, y, image=image)
        image = ImageTk.PhotoImage(self.buttons['reset'])
        if self.start: canvas.create_image(restartX, y, image=image)

    def drawSettings(self, canvas):
        canvas.create_rectangle(self.width-(self.width/4), self.barY,
                self.width, self.barY+(self.trueHeight/2), fill='darkgrey')
        fontSize = int(24*self.scale)
        font = 'Times', str(fontSize), 'bold'
        midX = (self.width*7)/8  # specific x coordinate
        canvas.create_text(midX, self.barY+(self.trueHeight/10), fill='black',
            anchor='center',  text='Difficulty:', font=font)
        boxes = self.getDifficultyBoxes()
        for i in range(3):  # three difficulties
            box = boxes[i]
            if (boxes[3][i].lower() == self.difficulty) and self.start and \
                    (not self.highlight): canvas.create_rectangle(self.width-
                    (self.width/4), box[1], self.width, box[3], fill='white')
            canvas.create_rectangle(box[0], box[1], box[2], box[3], fill='grey')
            if self.highlight and (self.highlight == box) and (not self.start):
                canvas.create_rectangle(box[0], box[1], box[2], box[3],
                                        fill='white')
                textFill = 'black'  # selected
            else: textFill = boxes[4][i]  # not selected
            canvas.create_text(midX, box[1]+((box[3]-box[1])/2), font=font,
                fill=textFill, activefill='black', anchor='center',
                text=boxes[3][i])

    def drawSky(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height,
                                fill='#34c0eb')
        for cloud in self.clouds: cloud.draw(canvas)

if __name__ == '__main__':
    JetpackScotty(width=800, height=450)
