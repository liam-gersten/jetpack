from cmu_112_graphics import *
import debugger
import chunkGeneration
from PIL import Image
import math, time, random, copy

def almostEqual(d1, d2, epsilon=10**-7): return (abs(d2-d1) < epsilon)

class Scotty():  # class for player
    def __init__(self, width, height, images, igniteImages):
        self.x = width/4
        self.y = height-100
        [self.sizeX, self.sizeY] = [35, 46]
        [self.up, self.airborne] = [False, True]
        self.images = images
        self.igniteImages = igniteImages

    def move(self, changeY, height):
        if self.sizeY/2 < self.y+changeY < (height-(self.sizeY/2)):
            self.y += changeY  # within bounds of game
        elif self.y+changeY >= height-(self.sizeY/2):
            self.airborne = False  # now running on the ground
            self.y = height-(self.sizeY/2)-5
            [self.sizeX, self.sizeY] = [52, 36]  # size of grounded sprites
        if self.y+(self.sizeY/2) > height:
            self.y = height-(self.sizeY/2)

    def draw(self, app, canvas, debug):
        if self.airborne: key = -1
        elif app.paused: key = 0
        else: key = int((time.time()*7*(app.speed/5))%3)  # ignite 1-15
        image = ImageTk.PhotoImage(self.images[key])
        canvas.create_image(self.x, self.y, image=image)
        if debug: debugger.outlineScotty(self, canvas)

    def drawFire(self, app, canvas):
        if self.up:
            startCoords = [self.x-12, self.y+(self.sizeY/2)]
            key = (int((time.time()-app.upInitial)*10))/10
            if key > 1.5: key = 1.5
            image = ImageTk.PhotoImage(self.igniteImages[key])
            y = startCoords[1]+((self.igniteImages[key].size[1])/2)
            canvas.create_image(startCoords[0], y, image=image)

class BackDrop():
    def __init__(self, app, index, x):
        self.x = x
        if index: self.x = (app.dropSize[0]/2)+(app.dropSize[0]*index)
        self.y = app.height-(app.dropSize[1]/2)
        self.key = random.choice([0, 1])

    def move(self, app): self.x -= app.speed//(app.dropMultiplier)

    def draw(self, app, canvas): canvas.create_image(self.x, self.y,
            image=app.getCachedPhotoImage(app.dropImages[self.key]))

class Coin():  # spinning coin object
    def __init__(self, app, row, col, chunkX):
        self.x = chunkX+(app.cellSize*col)+((app.coinSize+app.coinSpacing)/2)
        self.y = (app.cellSize*row)+((app.coinSize+app.coinSpacing)/2)

    def interacts(self, x, y, distance):  # can be more efficient
        if math.sqrt(((self.x-x)**2)+((self.y-y)**2)) <= distance: return True
        return False

    def draw(self, app, canvas, debug, sequence, size):
        coinId = int((time.time()*10)%7)  # ranges 0 - 6
        canvas.create_image(self.x, self.y,
                            image=app.getCachedPhotoImage(sequence[coinId]))
        if debug: canvas.create_rectangle(self.x-(size/2), self.y-(size/2),
                self.x+(size/2), self.y+(size/2), fill='')

class staticBeam():  # does not move
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        if (rows == 1) or (cols == 1):
            self.x1 = (col*app.cellSize)+chunkX+(app.cellSize/2)
            self.y1 = (row*app.cellSize)+(app.cellSize/2)
            self.x2 = ((col+cols-1)*app.cellSize)+chunkX+(app.cellSize/2)
            self.y2 = ((row+rows-1)*app.cellSize)+(app.cellSize/2)
        else:
            [first, second] = random.choice([[[rows-1, 0], [0, cols-1]],
                                             [[0, 0], [rows-1, cols-1]]])
            self.x1 = ((col+first[1])*app.cellSize)+chunkX+(app.cellSize/2)
            self.y1 = ((row+first[0])*app.cellSize)+(app.cellSize/2)
            self.x2 = ((col+second[1])*app.cellSize)+chunkX+(app.cellSize/2)
            self.y2 = ((row+second[0])*app.cellSize)+(app.cellSize/2)

    def move(self, app):
        self.x1 -= app.speed
        self.x2 -= app.speed

    def outOfBounds(self): return (self.x1+(self.width/3) < 0) and \
                                  (self.x2+(self.width/3) < 0)

    def interacts(self, app, player):
        pass

    def draw(self, app, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2,
                           fill='green', width=10)
        canvas.create_oval(self.x1-(self.width/3), self.y1-(self.width/3),
                self.x1+(self.width/3), self.y1+(self.width/3), fill='red')
        canvas.create_oval(self.x2-(self.width/3), self.y2-(self.width/3),
                self.x2+(self.width/3), self.y2+(self.width/3), fill='red')

class verticleBeam():  # initialize both to reduce duplicate code
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        self.centerY = ((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+self.xScale+self.width < 0

    def interacts(self, app, player):
        pass

    def draw(self, app, canvas):
        [x1, x2] = [self.centerX-self.xScale, self.centerX+self.xScale]
        yPosition = self.yScale*math.cos(2*math.pi*((time.time()-
                                            app.timeInitial)%1))
        y = self.centerY+yPosition
        canvas.create_line(x1, y, x2, y, fill='green', width=10)
        canvas.create_oval(x1-(self.width/3), y-(self.width/3),
                           x1+(self.width/3), y+(self.width/3), fill='red')
        canvas.create_oval(x2-(self.width/3), y-(self.width/3),
                           x2+(self.width/3), y+(self.width/3), fill='red')

class horizontalBeam():
    def __init__(self, app, rows, cols, row, col, chunkX):
        self.width = app.cellSize
        self.centerY = ((row+(rows/2))*app.cellSize)
        self.yScale = self.width*(rows-1)/2
        self.centerX = chunkX+((col+(cols/2))*app.cellSize)
        self.xScale = self.width*(cols-1)/2

    def move(self, app): self.centerX -= app.speed

    def outOfBounds(self): return self.centerX+(2*self.xScale)+self.width < 0

    def interacts(self, app, player):
        pass

    def draw(self, app, canvas):
        [y1, y2] = [self.centerY-self.yScale, self.centerY+self.yScale]
        xPosition = self.xScale*math.cos(2*math.pi*((time.time()-
                                            app.timeInitial)%1))
        x = self.centerX+xPosition
        canvas.create_line(x, y1, x, y2, fill='green', width=10)
        canvas.create_oval(x-(self.width/3), y1-(self.width/3),
                           x+(self.width/3), y1+(self.width/3), fill='red')
        canvas.create_oval(x-(self.width/3), y2-(self.width/3),
                           x+(self.width/3), y2+(self.width/3), fill='red')

class rotatingBeam():  # rotate left or right at constant speed
    def __init__(self, app, rows, cols, row, col, chunkX):
        pass

    def move(self, app):
        pass

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
        [self.sizeX, self.sizeY] = [26, 11]
        self.speedRange = [1, 1.5]
        self.sizeRange = [1, 2]
        self.coordsRange = app.height//3
        self.reDefine(app, random.randint(0, app.width))

    def reDefine(self, app, x):  # recreates new cloud at right end of screen
        self.sprite = app.loadImage('sprites/cloud0.png')
        if self.id % 2 == 0:
            self.sprite = self.sprite.transpose(Image.FLIP_LEFT_RIGHT)
        self.size = random.choice(self.sizeRange)
        self.speed = random.choice(self.speedRange)
        self.x = x
        self.y = random.randint(int(self.sizeY*self.size), self.coordsRange)
        self.sprite = app.scaleImage(self.sprite, self.size)

    def move(self, app):
        if self.x + (self.sizeX*self.size) < 0: self.reDefine(app, app.width)
        self.x -= self.speed

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
        [self.timerDelay, self.coinSize, self.coinSpacing] = [1, 16, 4]
        [self.dropMultiplier, self.cloudMultiplier] = [1.25, 4]
        [self.dDrops, self.dCoins] = [False, True]
        [self._mvcCheck, self.invincible] = [False, False]
        [self.rows, self.cols] = [20, 40]
        self.cellSize = self.width/self.cols
        self.cloudNumer = 3
        self.restartApp()

    def loadSprites(self):
        self.coinCoordsRange = [
            (self.width//(self.coinSize+self.coinSpacing)),
            (self.height//(self.coinSize+self.coinSpacing))]
        [self.coinSequence, self.igniteImages] = [{}, {}]
        self.igniteSpriteHeights = ()
        for i in range(4):
            image = self.loadImage('sprites/coin'+str(i)+'.png')
            self.coinSequence[i] = self.scaleImage(image, 1)  # temporary
        for i in range(2, -1, -1):
            image = self.loadImage('sprites/coin'+str(i)+'.png')
            image = self.scaleImage(image, 1)
            self.coinSequence[6 - i] = image.transpose(Image.FLIP_LEFT_RIGHT)
        self.scottyImages = {0: self.loadImage('sprites/scotty0.png'),
                             1: self.loadImage('sprites/scotty1.png'),
                             2: self.loadImage('sprites/scotty2.png'),
                             -1: self.loadImage('sprites/airborne.png')}
        dropImage = self.loadImage('sprites/cohon0.tiff')
        dropImage = self.scaleImage(dropImage, 2)
        self.dropSize = [dropImage.size[0], dropImage.size[1]]
        self.dropImages = {0: dropImage,
            1: dropImage.transpose(Image.FLIP_LEFT_RIGHT)}
        for i in range(16): self.igniteImages[i/10] = \
                self.loadImage('sprites/ignite'+str(i)+'.png')

    def restartApp(self):
        self.difficulty = 'medium'
        self.loadSprites()
        self.player = Scotty(self.width, self.height, self.scottyImages,
                             self.igniteImages)
        [self.points, self.movement, self.speed] = [0, 10, 2]
        [self.coins, self.clouds, self.beams, self.drops] = [[], [], [], []]
        [self.debug, self.paused] = [False, False]
        self.timeInitial = time.time()+1
        self.downInitial = time.time()-1
        self.upInitial = time.time()-1
        self.currentChunk = Chunk(self, False, 0)
        self.newChunk = Chunk(self, False, self.width)
        for i in range(self.cloudNumer): self.clouds += [Cloud(self, i)]
        for i in range((self.width//self.dropSize[0])+2):
            self.drops += [BackDrop(self, i, False)]

    def checkCoinInteraction(self):  # numpy will help here but is not required
        coinSpace = min([self.player.sizeX, self.player.sizeY])+self.coinSize/3
        newCoins = []
        for coin in self.coins:
            if coin.interacts(self.player.x, self.player.y, coinSpace):
                self.points += 1
            else: newCoins += [coin]
        self.coins = newCoins

    def getCachedPhotoImage(self, image):
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    def manageAll(self):
        [newCoins, newBeams] = [[], []]
        if self.newChunk.x <= 0:
            self.currentChunk = Chunk(self, self.newChunk.literal,
                                      self.newChunk.x)
            self.newChunk = Chunk(self, False, self.width)
        for coin in self.coins:
            if coin.x > (-self.coinSize): newCoins += [coin]
        for beam in self.beams:
            if not beam.outOfBounds(): newBeams += [beam]
        if self.drops[0].x+(self.dropSize[0]/2) < 0:
            self.drops = self.drops[1:]
            recentX = self.drops[-1].x+self.dropSize[0]
            self.drops += [BackDrop(self, False, recentX)]
        [self.coins, self.beams] = [newCoins, newBeams]
        self.checkCoinInteraction()

    def moveAll(self):
        self.newChunk.x -= self.speed
        self.currentChunk.x -= self.speed
        for cloud in self.clouds: cloud.move(self)
        for drop in self.drops: drop.move(self)
        for coin in self.coins: coin.x -= self.speed
        for beam in self.beams: beam.move(self)
        self.manageAll()

    def timerFired(self):
        if not self.paused: self.moveAll()
        # equation for Scotty velocity (make more efficient)
        if self.player.up: self.player.move(
            (-4*(time.time()-self.upInitial+1)**(1/2)), self.height)
        elif not self.paused: self.player.move((10*math.log(time.time()-
                            self.downInitial+1)), self.height)

    def mousePressed(self, event):
        if not self.player.up:
            [self.player.airborne, self.player.up] = [True, True]
            [self.player.sizeX, self.player.sizeY] = [35, 46]
            self.upInitial = time.time()+0

    def mouseReleased(self, event):
        if self.player.up:
            self.player.up = False
            self.downInitial = time.time()+0

    def keyPressed(self, event):
        if event.key.lower() == 'd': self.debug = not self.debug
        elif event.key.lower() == 'r': self.restartApp()
        elif event.key.lower() == 'up': self.speed += 1
        elif event.key.lower() == 'down': self.speed -= 1
        elif event.key.lower() == 'p': self.paused = not self.paused
        elif event.key.lower() == 'i': self.invincible = not self.invincible
        elif event.key.lower() == 'c': debugger.printer(self)
        elif event.key == '1': self.dDrops = not self.dDrops

    def redrawAll(self, canvas):
        self.drawSky(canvas)
        if self.dDrops:
            for drop in self.drops: drop.draw(self, canvas)
        if self.debug:
            debugger.drawBorders(self.currentChunk.x, self, canvas, 'red')
            debugger.drawBorders(self.newChunk.x, self, canvas, 'blue')
        self.player.draw(self, canvas, self.debug)
        self.player.drawFire(self, canvas)
        for coin in self.coins: coin.draw(self, canvas, self.debug,
                                          self.coinSequence, self.coinSize)
        for beam in self.beams: beam.draw(self, canvas)


    def drawSky(self, canvas):  # add art for CMU campus (Cohen UC)
        canvas.create_rectangle(0, 0, self.width, self.height, fill='#34c0eb')
        for cloud in self.clouds: cloud.draw(canvas)

if __name__ == '__main__':
    MyApp(width=800, height=400)
