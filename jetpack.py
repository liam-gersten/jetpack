from cmu_112_graphics import *
import printer
import chunkGeneration
from PIL import Image
import math, time, random, copy

def almostEqual(d1, d2, epsilon=10**-7): return (abs(d2-d1) < epsilon)

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

def drawBeam(app, canvas, x1, y1, angle1, x2, y2, angle2):
    widths = random.choice([[15, 12, 9, 6], [12, 10, 6, 4], [13, 13, 9, 5],
                            [14, 11, 7, 4]])
    canvas.create_line(x1, y1, x2, y2, fill='red4', width=widths[0]*app.scale)
    canvas.create_line(x1, y1, x2, y2, fill='red3', width=widths[1]*app.scale)
    canvas.create_line(x1, y1, x2, y2, fill='red2', width=widths[2]*app.scale)
    canvas.create_line(x1, y1, x2, y2, fill='red',  width=widths[2]*app.scale)


class Scotty():  # class for player
    def __init__(self, app, images, igniteImages):
        self.x = app.width/4
        self.y = app.height-(100*app.scale)
        [self.sizeX, self.sizeY] = [35*app.scale, 46*app.scale]
        [self.up, self.airborne] = [False, True]
        self.images = images
        self.igniteImages = igniteImages

    def move(self, app, changeY):
        if app.barY+self.sizeY/2 < self.y+changeY < (app.height-(self.sizeY/2)):
            self.y += changeY  # within bounds of game
        elif self.y+changeY >= app.height-(self.sizeY/2):
            self.airborne = False  # now running on the ground
            self.y = app.height-(self.sizeY/2)-(5*app.scale)
            [self.sizeX, self.sizeY] = [52*app.scale, 36*app.scale]
        if self.y+(self.sizeY/2) > app.height:
            self.y = app.height-(self.sizeY/2)

    def draw(self, app, canvas, debug):
        if self.airborne: key = -1
        elif app.paused: key = 0
        else: key = int((time.time()*7*(app.speed/5))%3)  # ignite 1-15
        image = ImageTk.PhotoImage(self.images[key])
        canvas.create_image(self.x, self.y, image=image)
        if debug: printer.outlineScotty(self, canvas)

    def drawFire(self, app, canvas):
        if self.up:  # rising
            startCoords = [self.x-(12*app.scale), self.y+(self.sizeY/2)]
            key = (int((time.time()-app.upInitial)*10))/10
            if key > 1.8: key = random.choice([1.5, 1.6, 1.7, 1.8])
            image = ImageTk.PhotoImage(self.igniteImages[key])
            y = startCoords[1]+((self.igniteImages[key].size[1])/2)
            canvas.create_image(startCoords[0], y, image=image)

class BackDrop():  # single sprite of Cohon University Center
    def __init__(self, app, index, x):
        self.x = x
        if index: self.x = (app.dropSize[0]/2)+(app.dropSize[0]*index)
        self.y = app.height-(app.dropSize[1]/2)
        self.key = random.choice([0, 1])

    def move(self, app): self.x -= app.speed//(app.dropMultiplier)

    def draw(self, app, canvas): canvas.create_image(self.x, self.y,
            image=app.getCachedPhotoImage(app.dropImages[self.key]))

class Coin():  # spinning coin object
    def __init__(self, app, row, col, chunkX, special):
        if not special:
            self.special = False
            self.x = chunkX+(app.cellSize*col)+\
                     ((app.coinSize+app.coinSpacing)/2)
            self.y = app.barY+(app.cellSize*row)+\
                     ((app.coinSize+app.coinSpacing)/2)
        else:
            self.special = True
            self.standardSize = app.buttonSizes/app.coinSequence[0].size[0]
            self.x = (app.buttonSizes/2)+app.buttonSpacing
            self.y = app.barY/2

    def changeTimeState(self, app):
        if time.time()-app.coinStart >= 1: app.coinStart = False

    def interacts(self, x, y, distance):  # player touches
        if math.sqrt(((self.x-x)**2)+((self.y-y)**2)) <= distance: return True
        return False

    def draw(self, app, canvas, debug, sequence, size):
        if (app.staticTime) and (not self.special): coinId = 1
        else: coinId = int((time.time()*10)%7)  # ranges 0 - 6
        if not self.special: image = app.getCachedPhotoImage(sequence[coinId])
        else:
            if app.coinStart:
                sizeScale = \
            self.standardSize*(1+math.sin(math.pi*(time.time()-app.coinStart)))
            else: sizeScale = self.standardSize
            image = app.getCachedPhotoImage(
                app.scaleImage(sequence[coinId], sizeScale))
        canvas.create_image(self.x, self.y, image=image)
        if debug: canvas.create_rectangle(self.x-(size/2), self.y-(size/2),
                self.x+(size/2), self.y+(size/2), fill='')

class staticBeam():  # does not move
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        if (rows == 1) or (cols == 1): [minus, first, second] = [1, 0, 0]
        else:
            minus = 0
            [first, second] = random.choice([[[rows-1, 0], [0, cols-1]],
                                             [[0, 0], [rows-1, cols-1]]])
        self.x1 = ((col+first[1])*app.cellSize)+chunkX+(app.cellSize/2)
        self.y1 = ((row+first[0])*app.cellSize)+(app.cellSize/2)+app.barY
        self.x2 = ((col+second[1]-minus)*app.cellSize)+chunkX+(app.cellSize/2)
        self.y2 = ((row+second[0]-minus)*app.cellSize)+(app.cellSize/2)+app.barY

    def move(self, app):
        self.x1 -= app.speed
        self.x2 -= app.speed

    def outOfBounds(self): return (self.x1+(self.width/3) < 0) and \
                                  (self.x2+(self.width/3) < 0)

    def interacts(self, app, player): return minDistance([self.x1, self.y1],
                [self.x2, self.y2], [player.x, player.y]) <= (player.sizeX/2)

    def draw(self, app, canvas):
        drawBeam(app, canvas, self.x1, self.y1, False, self.x2, self.y2, False)
        canvas.create_oval(self.x1-(self.width/3), self.y1-(self.width/3),
                self.x1+(self.width/3), self.y1+(self.width/3), fill='red')
        canvas.create_oval(self.x2-(self.width/3), self.y2-(self.width/3),
                self.x2+(self.width/3), self.y2+(self.width/3), fill='red')

class verticleBeam():  # moves vertically
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        self.centerY = app.barY+((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+self.xScale+self.width < 0

    def interacts(self, app, player):
        if app.staticTime: yPosition = self.yScale*math.cos(2*math.pi*((
            app.staticTime-app.timeSincePaused)%1))
        else: yPosition = self.yScale*math.cos(2*math.pi*((
            time.time()-app.timeSincePaused)%1))
        pa = [self.centerX-self.xScale, self.centerY+yPosition]
        pb = [self.centerX+self.xScale, self.centerY+yPosition]
        return minDistance(pa, pb, [player.x, player.y]) <= (player.sizeX/2)

    def draw(self, app, canvas):
        [x1, x2] = [self.centerX-self.xScale, self.centerX+self.xScale]
        if app.staticTime: yPosition = self.yScale*math.cos(2*math.pi*((
                app.staticTime-app.timeSincePaused)%1)) # animation curve
        else: yPosition = self.yScale*math.cos(2*math.pi*((
                time.time()-app.timeSincePaused)%1))
        y = self.centerY+yPosition
        drawBeam(app, canvas, x1, y, False, x2, y, False)
        canvas.create_oval(x1-(self.width/3), y-(self.width/3),
                           x1+(self.width/3), y+(self.width/3), fill='red')
        canvas.create_oval(x2-(self.width/3), y-(self.width/3),
                           x2+(self.width/3), y+(self.width/3), fill='red')

class horizontalBeam():  # moves horizontally
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        self.centerY = app.barY+((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+(2*self.xScale)+self.width < 0

    def interacts(self, app, player):
        if app.staticTime: xPosition = self.xScale*math.cos(2*math.pi*((
                    app.staticTime-app.timeSincePaused)%1))
        else: xPosition = self.xScale*math.cos(2*math.pi*
                    ((time.time()-app.timeSincePaused)%1))
        pa = [self.centerX+xPosition, self.centerY-self.yScale]
        pb = [self.centerX+xPosition, self.centerY+self.yScale]
        return minDistance(pa, pb, [player.x, player.y]) <= (player.sizeX/2)

    def draw(self, app, canvas):
        [y1, y2] = [self.centerY-self.yScale, self.centerY+self.yScale]
        if app.staticTime: xPosition = self.xScale*math.cos(2*math.pi*((
                    app.staticTime-app.timeSincePaused)%1))
        else: xPosition = self.xScale*math.cos(2*math.pi* # animation curve
                    ((time.time()-app.timeSincePaused)%1))
        x = self.centerX+xPosition
        drawBeam(app, canvas, x, y1, False, x, y2, False)
        canvas.create_oval(x-(self.width/3), y1-(self.width/3),
                           x+(self.width/3), y1+(self.width/3), fill='red')
        canvas.create_oval(x-(self.width/3), y2-(self.width/3),
                           x+(self.width/3), y2+(self.width/3), fill='red')

class rotatingBeam():  # rotate left or right
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        self.centerY = app.barY+((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+(2*self.xScale)+self.width < 0

    def interacts(self, app, player):
        if app.staticTime:
            timeStamp = 2*((app.staticTime-app.timeSincePaused)%1)
        else: timeStamp = 2*((time.time()-app.timeSincePaused)%1)
        angle = math.pi+(math.pi*(math.cos((timeStamp*math.pi)/2)))
        [dy, dx] = [self.yScale*math.sin(angle),
                    self.yScale*math.cos(angle)]
        return minDistance([(self.centerX-dx), (self.centerY-dy)],
            [(self.centerX+dx), (self.centerY+dy)], [player.x, player.y]) <= \
               (player.sizeX/2)

    def draw(self, app, canvas):  # animation curve below
        if app.staticTime:
            timeStamp = 2*((app.staticTime-app.timeSincePaused)%1)
        else: timeStamp = 2*((time.time()-app.timeSincePaused)%1)
        angle = math.pi+(math.pi*(math.cos((timeStamp*math.pi)/2)))
        if almostEqual(angle, 2*math.pi): angle = 0
        [dy, dx] = [self.yScale*math.sin(angle), self.yScale*math.cos(angle)]
        [x1, y1, x2, y2] = [self.centerX-dx, self.centerY-dy,
                            self.centerX+dx, self.centerY+dy]
        drawBeam(app, canvas, x1, y1, False, x2, y2, False)
        canvas.create_oval(x1-(self.width/3), y1-(self.width/3),
                           x1+(self.width/3), y1+(self.width/3), fill='red')
        canvas.create_oval(x2-(self.width/3), y2-(self.width/3),
                           x2+(self.width/3), y2+(self.width/3), fill='red')

class missile():
    def __init__(self, app, x, y):
        [self.x, self.y] = [x, y]  # load sprites

    def updateCoords(self, app):
        pass

    def draw(self, app, canvas):  #  waves from sin(time.time()-timeInitial)
        pass

class dragon():
    def __init__(self, app, x, y):
        pass

    def updateCoords(self, app):
        pass

    def draw(self, app, canvas):
        pass

    def drawLimb(self, app, canvas):
        pass

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
        if self.x + (self.sizeX*self.size) < 0: self.reDefine(app, app.width)
        self.x -= self.speed//app.cloudMultiplier

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

class MyApp(App):
    def appStarted(self):
        [self._mvcCheck, self.invincible] = [True, False]
        [self.rows, self.cols] = [20, 40]
        [self.difficulty, self.difficultyBase, self.diffInc] = ['medium', 50, 5]
        self.pathfinderStall = 0.5
        [self.cloudNumer, self.longestRun, self.currentRun] = [3, 0, 0]
        [self.barPortion, self.standardizedWidth] = [9, 800]
        self.scale = self.width/self.standardizedWidth
        self.barY = (self.height//self.barPortion)
        self.buttonSizes = (2*self.barY)//3
        self.buttonSpacing = (self.barY-self.buttonSizes)//2
        if self.width <= 400: self.buttonSizes = self.barY
        self.trueHeight = self.height-self.barY
        self.cellSize = self.width/self.cols
        [self.dDrops, self.dCoins] = [False, True]
        [self.timerDelay, self.coinSize, self.coinSpacing] = \
            [1, 16*self.scale, 4*self.scale]
        [self.dropMultiplier, self.cloudMultiplier] = [1.25, 2]
        self.restartApp()

    def loadIndividualSprites(self):
        self.scottyImages = {-1: self.loadImage('sprites/airborne.png')}
        [self.coinSequence, self.igniteImages, self.buttons] = [{}, {}, {}]
        self.buttons['pause'] = self.loadImage('sprites/pause.png')
        self.buttons['play'] = self.loadImage('sprites/play.png')
        self.buttons['exit'] = self.loadImage('sprites/exit.png')
        self.buttons['reset'] = self.loadImage('sprites/reset.png')
        self.buttons['settings'] = self.loadImage('sprites/settings.png')

    def loadSprites(self):  # called only once
        self.loadIndividualSprites()
        self.coinCoordsRange = [
            (self.width//(self.coinSize+self.coinSpacing)),
            (self.trueHeight//(self.coinSize+self.coinSpacing))]
        for i in range(4):
            image = self.loadImage('sprites/coin'+str(i)+'.png')
            self.coinSequence[i] = self.scaleImage(image, self.scale)
        for i in range(2, -1, -1):
            image = self.loadImage('sprites/coin'+str(i)+'.png')
            image = self.scaleImage(image, self.scale)
            self.coinSequence[6-i] = image.transpose(Image.FLIP_LEFT_RIGHT)
        for i in range(3): self.scottyImages[i] = \
            self.loadImage('sprites/scotty'+str(i)+'.png')
        for imageKey in self.scottyImages:
            self.scottyImages[imageKey] = \
                self.scaleImage(self.scottyImages[imageKey], self.scale)
        dropImage = self.loadImage('sprites/cohon0.tiff')
        dropImage = self.scaleImage(dropImage, 2*self.scale)
        self.dropSize = [dropImage.size[0], dropImage.size[1]]
        self.dropImages = {0: dropImage,
            1: dropImage.transpose(Image.FLIP_LEFT_RIGHT)}
        for i in range(17): self.igniteImages[i/10] = self.scaleImage(
            self.loadImage('sprites/ignite'+str(i)+'.png'), self.scale)
        self.igniteImages[1.7] = self.igniteImages[1.5].\
            transpose(Image.FLIP_LEFT_RIGHT)
        self.igniteImages[1.8] = self.igniteImages[1.6].\
            transpose(Image.FLIP_LEFT_RIGHT)
        for button in self.buttons:
            scale = self.buttonSizes/self.buttons[button].size[0]
            self.buttons[button] = self.scaleImage(self.buttons[button], scale)

    def restartApp(self):
        # printer.tp1ReadMe()
        if self.currentRun > self.longestRun: self.longestRun = self.currentRun
        [self.currentRun, self.points] = [0, 0]
        [self.debug, self.paused, self.settingsOpen] = [False, False, False]
        [self.kill, self.firstChunk] = [False, True]
        self.loadSprites()
        [self.movement, self.speed] = [10*self.scale, 2*self.scale]
        [self.coinStart, self.staticTime, self.gameOver] = [False, False, False]
        [self.downInitial, self.upInitial, self.timeSincePaused,
         self.timeInitial] = [time.time()-1, time.time()-1, time.time()-1,
                              time.time()+1]
        self.player = Scotty(self, self.scottyImages, self.igniteImages)
        [self.coins, self.clouds, self.beams, self.drops] = [[], [], [], []]
        self.specialCoin = Coin(self, False, False, False, True)
        self.currentChunk = Chunk(self, False, 0)
        self.firstChunk = False
        self.newChunk = Chunk(self, False, self.width)
        for i in range(self.cloudNumer): self.clouds += [Cloud(self, i)]
        for i in range((self.width//self.dropSize[0])+2):
            self.drops += [BackDrop(self, i, False)]

    def checkCoinInteraction(self):  # calls .interacts methods for coins
        coinSpace = min([self.player.sizeX, self.player.sizeY])+self.coinSize/3
        newCoins = []
        for coin in self.coins:
            if coin.interacts(self.player.x, self.player.y, coinSpace):
                self.points += 1
                self.coinStart = time.time()
            else: newCoins += [coin]
        self.coins = newCoins

    def getCachedPhotoImage(self, image):
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def killAll(self):
        [self.gameOver, self.paused] = [True, True]
        self.staticTime = time.time()+0
        [self.killXSize, self.killYSize] = [self.width/4, self.trueHeight/4]
        [self.miniXSize, self.miniYSize] = [(9*self.killXSize)/10,
                                            (9*self.killYSize)/10]
        [self.killX, self.killY] = [self.width/2, self.height+self.killYSize]

    def manageAll(self):  # deletes and adds objects based on locations
        [newCoins, newBeams, kill] = [[], [], False]
        if self.newChunk.x <= 0:
            self.currentChunk = Chunk(self, self.newChunk.literal,
                                      self.newChunk.x)
            self.newChunk = Chunk(self, False, self.width)
        for coin in self.coins:
            if coin.x > (-self.coinSize): newCoins += [coin]
        for beam in self.beams:
            if (not self.invincible) and (beam.interacts(self, self.player)):
                kill = True
            if not beam.outOfBounds(): newBeams += [beam]
        if self.drops[0].x+(self.dropSize[0]/2) < 0:
            self.drops = self.drops[1:]
            recentX = self.drops[-1].x+self.dropSize[0]
            self.drops += [BackDrop(self, False, recentX)]
        [self.coins, self.beams] = [newCoins, newBeams]
        if kill: self.killAll()
        self.checkCoinInteraction()

    def moveAll(self):  # moves all objects at various speeds
        self.currentRun += self.speed
        self.newChunk.x -= self.speed
        self.currentChunk.x -= self.speed
        for cloud in self.clouds: cloud.move(self)
        for drop in self.drops: drop.move(self)
        for coin in self.coins: coin.x -= self.speed
        for beam in self.beams: beam.move(self)
        self.manageAll()

    def timerFired(self):
        if self.gameOver and (self.killY > (self.trueHeight/2)+self.barY):
            self.killY -= 5*self.scale
        self.specialCoin.changeTimeState(self)
        if not self.paused: self.moveAll()
        if self.player.up: self.player.move(self,
            (-4*self.scale*(time.time()-self.upInitial+1)**(1/2)))
        elif (not self.paused) or self.gameOver: self.player.move(self,
                    (self.scale*10*math.log(time.time()-self.downInitial+1)))

    def mousePressed(self, event):
        if ((self.barY-self.buttonSizes)/2) <= event.y <= self.barY-\
                ((self.barY-self.buttonSizes)/2):
            if self.width-self.buttonSpacing-self.buttonSizes <= event.x <= \
                    self.width-self.buttonSpacing:
                self.paused = not self.paused
                if self.paused: self.staticTime = time.time()+0
                else:
                    self.timeSincePaused = time.time()
                    self.staticTime = False
            if self.width-(2*(self.buttonSpacing+self.buttonSizes)) <= event.x \
                    <= self.width-(2*self.buttonSpacing)-self.buttonSizes:
                self.restartApp()
            if self.width-(3*(self.buttonSpacing+self.buttonSizes)) <= event.x \
                    <= self.width-(3*self.buttonSpacing)-(2*self.buttonSizes):
                self.settingsOpen = not self.settingsOpen
                self.paused = not self.paused
                if self.paused: self.staticTime = time.time()+0
                else:
                    self.timeSincePaused = time.time()
                    self.staticTime = False
        elif (not self.player.up) and (not self.paused):  # falling
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
        elif event.key.lower() == 'up': self.speed += 1
        elif event.key.lower() == 'down': self.speed -= 1
        elif event.key.lower() == 'right': self.difficultyBase += self.diffInc
        elif (event.key.lower() == 'left') and (self.difficultyBase-
                        self.diffInc > 0): self.difficultyBase -= self.diffInc
        elif event.key.lower() == 'i': self.invincible = not self.invincible
        elif event.key.lower() == 'c': printer.printer(self)
        elif event.key == '1': self.dDrops = not self.dDrops  # display Cohon

    def redrawAll(self, canvas):
        self.drawSky(canvas)
        if self.dDrops:
            for drop in self.drops: drop.draw(self, canvas)
        if self.debug:
            printer.drawBorders(self.currentChunk.x, self, canvas, 'red')
            printer.drawBorders(self.newChunk.x, self, canvas, 'blue')
        self.player.draw(self, canvas, self.debug)
        self.player.drawFire(self, canvas)
        for coin in self.coins: coin.draw(self, canvas, self.debug,
                                          self.coinSequence, self.coinSize)
        for beam in self.beams: beam.draw(self, canvas)
        self.drawStatusBar(canvas)
        if self.gameOver: self.drawGameOver(canvas)

    def drawGameOver(self, canvas):
        box1 = [self.killX-self.killXSize, self.killY-self.killYSize,
                self.killX+self.killXSize, self.killY+self.killYSize]
        box2 = [self.killX-self.miniXSize, self.killY-self.miniYSize,
                self.killX+self.miniXSize, self.killY+self.miniYSize]
        fontSize = 50*(self.width//self.standardizedWidth)
        font = 'Times', str(fontSize), 'bold'
        canvas.create_rectangle(box1[0], box1[1], box1[2], box1[3],
                                fill='darkgrey')
        canvas.create_rectangle(box2[0], box2[1], box2[2], box2[3], fill='grey')
        canvas.create_text(self.killX, self.killY-(self.killYSize/5),
            fill='red', text='Game Over!', anchor='center', font=font)

    def drawStatusBar(self, canvas):
        self.drawButtons(canvas)
        self.drawUpperCoin(canvas)
        self.drawCurrentRun(canvas)

    def drawUpperCoin(self, canvas):
        xPosition = (3*self.buttonSpacing)+self.buttonSizes
        font = 'Times', str(int(24*self.scale)), 'bold italic'
        canvas.create_text(xPosition, self.barY/2, activefill='gold',
                    fill='black', text=self.points, anchor='w', font=font)
        self.specialCoin.draw(self, canvas, self.debug, self.coinSequence,
                              self.coinSize)

    def drawCurrentRun(self, canvas):
        xPosition = self.width/2
        fontSize = 24*(self.width//self.standardizedWidth)
        font = 'Times', str(fontSize), 'bold'
        if self.currentRun >= self.longestRun:
            text = 'High Score! '+str(self.currentRun//100)+'m'
            colors = ['darkgrey', 'gold']
        else:
            text = 'Current Run '+str(self.currentRun//100)+'m'
            colors = ['lightgrey', 'black']
        canvas.create_rectangle(xPosition-4*self.buttonSizes,
            self.buttonSpacing, xPosition+4*self.buttonSizes,
            self.barY-self.buttonSpacing, fill=colors[0])
        canvas.create_text(xPosition, self.barY/2, activefill='gold',
                    fill=colors[1], text=text, anchor='center', font=font)

    def drawButtons(self, canvas):
        y = self.barY//2
        pausedX = self.width-self.buttonSpacing-(self.buttonSizes//2)
        restartX = self.width-(2*self.buttonSpacing)-((3*self.buttonSizes)//2)
        settingsX = self.width-(3*self.buttonSpacing)-((5*self.buttonSizes)//2)
        if self.paused: image = ImageTk.PhotoImage(self.buttons['play'])
        else: image = ImageTk.PhotoImage(self.buttons['pause'])
        canvas.create_image(pausedX, y, image=image)
        if self.settingsOpen: image = ImageTk.PhotoImage(self.buttons['exit'])
        else: image = ImageTk.PhotoImage(self.buttons['settings'])
        canvas.create_image(settingsX, y, image=image)
        image = ImageTk.PhotoImage(self.buttons['reset'])
        canvas.create_image(restartX, y, image=image)

    def drawSky(self, canvas):
        canvas.create_rectangle(0, self.barY, self.width, self.height,
                                fill='#34c0eb')
        for cloud in self.clouds: cloud.draw(canvas)

if __name__ == '__main__':
    MyApp(width=800, height=450)  # cohon doesn't move below 400 x 250
