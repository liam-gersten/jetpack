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