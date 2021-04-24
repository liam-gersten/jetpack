from cmu_112_graphics import *
from debugger import *
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
        if debug: outlineScotty(self, canvas)

    def drawFire(self, app, canvas):
        if self.up:
            startCoords = [self.x-12, self.y+(self.sizeY/2)]
            key = (int((time.time()-app.upInitial)*10))/10
            if key > 1.5: key = 1.5
            image = ImageTk.PhotoImage(self.igniteImages[key])
            y = startCoords[1]+((self.igniteImages[key].size[1])/2)
            canvas.create_image(startCoords[0], y, image=image)

class BackDrop():
    def __init__(self, app, index):
        self.x = app.width + (app.dropImages[0].size[0] / 2)
        if index: self.x = app.width+(app.dropImages[0].size[0]/2)+\
                           (app.dropImages[0].size[0]*index)
        self.y = app.height-(app.dropImages[0].size[1]/2)
        self.key = random.choice([0, 1])

    def move(self, app): self.x -= app.speed/(app.dropMultiplier)

    def draw(self, app, canvas):
        canvas.create_image(self.x, self.y, image=app.getCachedPhotoImage(
            app.dropImages[self.key]))

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

    def updateCoords(self, app):
        self.x1 -= app.speed
        self.x2 -= app.speed

class verticleBeam():  # move up and down with sin waves
    def __init__(self, app, rows, cols, row, col, chunkX):
        pass

    def updateCoords(self, app):
        pass

class rotatingBeam():  # rotate left or right at constant speed
    def __init__(self, app, rows, cols, row, col, chunkX):
        pass

    def updateCoords(self, app):
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
            [self.literal, self.x] = [[], x]
            # preliminary generation without pathfinder or complexity
            for row in range(app.rows):
                currentRow = []
                for col in range(app.cols): currentRow += ['']
                self.literal += [currentRow]
            for i in range(random.randint(1, 2)):
                coinChunk = self.generateChunk(app, [[2, 3], [2, 3]], [])
                if not coinChunk: break
                self.modifyBoard(app, coinChunk, app.coins, 'c')
            for i in range(1):
                beamChunk = self.generateChunk(app, [[1, 4], [1, 4]], [])
                if not beamChunk: break
                self.modifyBoard(app, beamChunk, [], [])
                app.beams += [staticBeam(app, len(beamChunk[0]),
                    len(beamChunk[0][0]), beamChunk[1], beamChunk[2], self.x)]

    def modifyBoard(self, app, chunk, storeList, version):  # destructive
        for row in range(len(chunk[0])):
            for col in range(len(chunk[0][0])):
                if version == 'c':
                    object = Coin(app, row+chunk[1], col+chunk[2], self.x)
                if version == []: object = []
                self.literal[row+chunk[1]][col+chunk[2]] = version
                storeList += [object]

    def checkAvalibility(self, app, coinList, startRow, startCol):
        for row in range(len(coinList)):
            for col in range(len(coinList[row])):
                if (row+startRow >= app.rows) or (col+startCol >= app.cols) or \
                        (self.literal[row+startRow][col+startCol] != ''):
                    return False
        return True

    def generateChunk(self, app, ranges, chunk):  # makes mini chunk
        loopNumber = 0
        while True:
            if loopNumber > 50: return False  # for efficiency
            [rows, cols] = [random.randrange(ranges[1][0], ranges[1][1]),
                            random.randrange(ranges[0][0], ranges[0][1])]
            for row in range(rows):
                currentRow = []
                for col in range(cols): currentRow += [1]
                chunk.append(currentRow)
            [row, col] = [random.randint(0, app.rows-1),
                          random.randint(0, app.cols-1)]
            if self.checkAvalibility(app, chunk, row, col): break
            loopNumber += 1
        return [chunk, row, col]

class MyApp(App):
    def appStarted(self):
        tp0ReadMe()
        [self.timerDelay, self.coinSize, self.coinSpacing] = [5, 16, 4]
        [self.dropMultiplier, self.cloudMultiplier] = [1, 4]
        [self.rows, self.cols] = [20, 40]
        self._mvcCheck = False
        self.cellSize = self.width/self.cols
        self.cloudNumer = 3
        self.invincible = False
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
        dropImage = self.loadImage('sprites/cohon0.png')
        self.scaleImage(dropImage, 10)
        self.dropImages = {0: dropImage,
                           1: dropImage.transpose(Image.FLIP_LEFT_RIGHT)}
        for i in range(16): self.igniteImages[i/10] = \
                self.loadImage('sprites/ignite'+str(i)+'.png')

    def restartApp(self):
        self.loadSprites()
        self.player = Scotty(self.width, self.height, self.scottyImages,
                             self.igniteImages)
        [self.points, self.movement, self.speed] = [0, 10, 5]
        [self.coins, self.clouds, self.beams, self.drops] = [[], [], [], []]
        [self.debug, self.paused] = [False, False]
        self.currentChunk = Chunk(self, False, 0)
        self.newChunk = Chunk(self, False, self.width)
        self.downInitial = time.time()-1
        self.upInitial = time.time()-1
        for i in range(self.cloudNumer): self.clouds += [Cloud(self, i)]
        for i in range(self.width//self.dropImages[0].size[0]):
            self.drops += [BackDrop(self, i)]

    def beamInteracts(self, beam, x, y, distance):
        pass  # numpy will help here but is not required

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

    def moveAll(self):  # reduce duplicate code
        if self.newChunk.x <= 0:
            self.currentChunk = Chunk(self, self.newChunk.literal,
                                      self.newChunk.x)
            self.newChunk = Chunk(self, False, self.width)
        self.newChunk.x -= self.speed
        self.currentChunk.x -= self.speed
        [newCoins, newBeams, newDrops] = [[], [], []]
        for cloud in self.clouds: cloud.move(self)
        for drop in self.drops:
            drop.move(self)
            if drop.x+(self.dropImages[0].size[0]/2) > 0: newDrops += [drop]
        for coin in self.coins:
            coin.x -= self.speed
            if coin.x > (-self.coinSize): newCoins += [coin]
        for beam in self.beams:
            self.beamInteracts(beam, self.player.x, self.player.y,
                    min([self.player.sizeX, self.player.sizeY]))
            beam.x1 -= self.speed
            beam.x2 -= self.speed
            if (beam.x1 > 0) or (beam.x2 > 0): newBeams += [beam]
        if len(self.drops)-len(newDrops) == 1:
            newDrops += [BackDrop(self, False)]
        [self.coins, self.beams, self.drops] = [newCoins, newBeams, newDrops]
        self.checkCoinInteraction()

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
        elif event.key.lower() == 'c': printer(self)

    def redrawAll(self, canvas):
        self.drawSky(canvas)
        if self.debug:
            drawBorders(self.currentChunk.x, self, canvas, 'red')
            drawBorders(self.newChunk.x, self, canvas, 'blue')
        for drop in self.drops: drop.draw(self, canvas)
        self.player.draw(self, canvas, self.debug)
        self.player.drawFire(self, canvas)
        for coin in self.coins: coin.draw(self, canvas, self.debug,
                                          self.coinSequence, self.coinSize)
        for beam in self.beams:
            self.drawBeam(beam, canvas)
            self.drawEnds(beam, canvas)

    # to be replaced by images
    def drawBeam(self, beam, canvas): canvas.create_line(beam.x1, beam.y1,
                    beam.x2, beam.y2, fill='green', width=10)

    def drawEnds(self, beam, canvas):  # to be replaced by images
        canvas.create_oval(beam.x1-(beam.width/3), beam.y1-(beam.width/3),
                    beam.x1+(beam.width/3), beam.y1+(beam.width/3), fill='red')
        canvas.create_oval(beam.x2-(beam.width/3), beam.y2-(beam.width/3),
                    beam.x2+(beam.width/3), beam.y2+(beam.width/3), fill='red')

    def drawSky(self, canvas):  # add art for CMU campus (Cohen UC)
        canvas.create_rectangle(0, 0, self.width, self.height, fill='#34c0eb')
        for cloud in self.clouds: cloud.draw(canvas)

MyApp(width=800, height=400)
