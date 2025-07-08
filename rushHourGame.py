import pygame
import number
import time
import tracemalloc
from vehicle import Vehicle, Board
from gameModels import GameState, Algorithm
from ui import Button, Dropdown
from colors import Colors

background = pygame.image.load("Resource/starBG.jpeg")
background = pygame.transform.scale(background, (number.WINDOWWIDTH, number.WINDOWHEIGHT))

pygame.init()

class RushHourGame:
    def __init__(self):
        self.screenWidth = number.WINDOWWIDTH
        self.screenHeight = number.WINDOWHEIGHT
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        
        pygame.display.set_caption("Rush Hour Solver")
        icon = pygame.image.load("Resource/icon.png")
        pygame.display.set_icon(icon)
        
        self.running = True
        self.gameState = GameState.STOPPED
        
        self.titleFont = pygame.font.Font(None, 48)
        self.buttonFont = pygame.font.Font(None, 36)
        self.mediumFont = pygame.font.Font(None, 32)
        self.smallFont = pygame.font.Font(None, 24)
        
        self.gridSize = 6
        self.cellSize = 90
        self.gridPadding = 20
        
        self.layout()
        
        self.vehicles = []
        self.board = None
        self.initialState = None
        self.currentAlgorithm = Algorithm.BFS
        self.currentMap = "level1.txt"
        self.availableMaps = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", "level5.txt",
                              "level6.txt","level7.txt","level8.txt","level9.txt","level10.txt", "level11.txt", "level12.txt"]
        
        self.animationSpeed = 1.5
        self.solutionPath = []
        self.currentStep = 0
        self.lastMoveTime = 0
        
        self.searchTime = 0.0
        self.nodesExpanded = 0
        self.peakMemoryKb = 0.0
        self.solutionMoves = []
        self.totalCost = 0
        
        self.loadAssets()
        
        self.setupUI()
        self.loadMap(self.currentMap)
    
    def layout(self):
        self.headerHeight = 80
        
        self.columnPadding = 2
        self.cardPadding = 20
        
        usableWidth = self.screenWidth - (4 * self.columnPadding)
        
        self.leftColumnWidth = int(usableWidth * 0.20)
        self.leftColumnX = 30
        self.leftColumnY = 90
        
        self.centerColumnWidth = int(usableWidth * 0.60)
        self.centerColumnX = self.leftColumnX + self.leftColumnWidth + self.columnPadding - 50
        self.centerColumnY = self.leftColumnY
        
        self.rightColumnWidth = int(usableWidth * 0.22)
        self.rightColumnX = number.WINDOWWIDTH - self.rightColumnWidth - 50
        self.rightColumnY = self.leftColumnY

        gridWidth = self.gridSize * self.cellSize + (self.gridPadding * 2)
        self.gridX = self.centerColumnX + (self.centerColumnWidth - gridWidth) // 2
        
        self.gridCardWidth = gridWidth + (self.cardPadding * 2)
        self.gridCardHeight = gridWidth + (self.cardPadding * 2) + 50
        self.gridCardX = self.centerColumnX + (self.centerColumnWidth - self.gridCardWidth) // 2
        
        centerColumnAvailableHeight = self.screenHeight - self.headerHeight - (2 * self.columnPadding)
        # self.gridCardY = self.headerHeight + self.columnPadding + ((centerColumnAvailableHeight - self.gridCardHeight) // 2)
        self.gridCardY = 90
        self.gridY = self.gridCardY + self.gridPadding + 50
    
    def loadAssets(self):
        self.resetIcon = pygame.image.load("Resource/reset.png")
        self.resetIcon = pygame.transform.scale(self.resetIcon, (20, 20))
        
        self.carImages = []
        for i in range(1, 9):
            image = pygame.image.load(f"Resource/car{i}.png")
            self.carImages.append(image)
                
        self.truckImages = []
        for i in range(1, 8):
            image = pygame.image.load(f"Resource/truck{i}.png")
            self.truckImages.append(image)
        
        self.targetCarImage = pygame.image.load("Resource/target.png")
        
    def setupUI(self):
        controlCardX = self.leftColumnX
        controlCardY = self.leftColumnY
        
        self.controlCardWidth = self.leftColumnWidth
        self.controlCardHeight = 500
        
        contentX = controlCardX + 20
        contentY = controlCardY + 70
        buttonWidth = self.controlCardWidth - 40
        buttonHeight = 50
        buttonSpacing = 25
        dropdownHeight = 45
        
        algorithms = [alg.value for alg in Algorithm]
        self.algorithmDropdown = Dropdown(
            contentX, contentY+20, buttonWidth, dropdownHeight,
            "Algorithm", self.mediumFont, algorithms
        )
        
        self.mapDropdown = Dropdown(
            contentX, contentY + dropdownHeight + buttonSpacing * 2+20, 
            buttonWidth, dropdownHeight, "Map",
             self.mediumFont, self.availableMaps,
        )
        
        self.playButton = Button(
            contentX, contentY + (dropdownHeight + buttonSpacing) * 3,
            buttonWidth, buttonHeight,
            "Solve", self.buttonFont, self.playGame
        )
        
        actionButtonsY = contentY + (dropdownHeight + buttonSpacing) * 3 + buttonHeight + buttonSpacing
        resetBtnSize = 50
        
        self.pauseButton = Button(
            contentX, 
            actionButtonsY,
            buttonWidth - resetBtnSize - 10, resetBtnSize,
            "Pause", self.mediumFont, self.pauseGame
        )
        
        self.resetButton = Button(
            contentX + buttonWidth - resetBtnSize, 
            actionButtonsY,
            resetBtnSize, resetBtnSize,
            "", self.buttonFont, self.resetGame, self.resetIcon
        )
        
        backBtnY = controlCardY + self.controlCardHeight - 70
        self.backButton = Button(
            contentX, backBtnY, buttonWidth, 40,
            "Back to Menu", self.mediumFont, self.backToMenu
        )
        
        self.buttons = [
            self.playButton, self.pauseButton, self.resetButton,
            self.backButton
        ]
        
        self.dropdowns = [self.algorithmDropdown, self.mapDropdown]
    
    def backToMenu(self):
        number.currentScreen = 0
    
    def loadMap(self, filename):
        self.vehicles = []
        
        with open(filename, 'r') as file:
            lines = file.readlines()
            
        carId = 0
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) == 4:
                    x, y, size, orientation = int(parts[0]), int(parts[1]), int(parts[2]), parts[3]
                    self.vehicles.append(Vehicle(carId, x, y, size, orientation == 'H'))
                    carId += 1
            
        
        
        self.board = Board(self.vehicles)
        self.initialState = tuple([coord for v in self.vehicles for coord in (v.row, v.col)])
        
        self.originalPositions = [(vehicle.row, vehicle.col) for vehicle in self.vehicles]
    
    def playGame(self):
        if self.gameState == GameState.STOPPED:
            self.runAlgorithm(self.currentAlgorithm)
        elif self.gameState == GameState.PAUSED:
            self.gameState = GameState.PLAYING
    
    def runAlgorithm(self, algorithm):
        if not self.board or not self.initialState:
            print("No board or initial state available")
            return
        
        algorithm_names = {
            Algorithm.A_STAR: "A*",
            Algorithm.BFS: "BFS",
            Algorithm.IDS: "IDS (Iterative Deepening Search)",
            Algorithm.UCS: "UCS (Uniform-Cost Search)"
        }
        
        algo_name = algorithm_names.get(algorithm, "Unknown")
        print(f"Running {algo_name} algorithm...")
        self.gameState = GameState.PLAYING
        
        tracemalloc.start()
        startCurrent, startPeak = tracemalloc.get_traced_memory()
        startTime = time.time()
        
        try:
            if algorithm == Algorithm.A_STAR:
                result = self.board.aStar(self.initialState)
            elif algorithm == Algorithm.BFS:
                result = self.board.bfs(self.initialState)
            elif algorithm == Algorithm.IDS:
                result = self.board.ids(self.initialState, max_depth=100)
            elif algorithm == Algorithm.UCS:
                result = self.board.ucs(self.initialState)
            else:
                result = self.board.aStar(self.initialState)
            
            endTime = time.time()
            endCurrent, endPeak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            self.searchTime = endTime - startTime
            self.nodesExpanded = self.board.nodesExpanded
            self.peakMemoryKb = (endPeak - startCurrent) / 1024
            
            if result is None:
                error_msg = "No solution found within depth limit!" if algorithm == Algorithm.IDS else "No solution found!"
                print(error_msg)
                self.solutionPath = [f"No solution found with {algo_name}" + (" (depth limit exceeded)" if algorithm == Algorithm.IDS else "")]
                self.solutionMoves = []
                self.totalCost = 0
                self.gameState = GameState.FINISHED
                return
            
            if algorithm in [Algorithm.A_STAR, Algorithm.UCS]:
                moves, self.totalCost = result
            else:
                moves = result
                self.totalCost = sum(self.vehicles[vid].length for vid, _ in moves)
            
            print(f"{algo_name} Solution found in {self.searchTime:.3f}s with {len(moves)} moves")
            print(f"Total cost: {self.totalCost}")
            print(f"Nodes expanded: {self.nodesExpanded}")
            print(f"Peak memory usage: {self.peakMemoryKb:.2f} KB")
            
            self.solutionMoves = moves
            self.solutionPath = []
            self.currentGameState = self.initialState
            
            for vid, delta in moves:
                vehicleName = f"Car {vid}" if vid != 0 else "Target Car"
                direction = ""
                
                if self.vehicles[vid].isHorizontal:
                    direction = "right" if delta > 0 else "left"
                else:
                    direction = "down" if delta > 0 else "up"
                
                moveDesc = f"{vehicleName} moves {abs(delta)} cell{'s' if abs(delta) > 1 else ''} {direction}"
                self.solutionPath.append(moveDesc)
            
            self.solutionPath.append("Target reached!")
            
        except Exception as e:
            tracemalloc.stop()
            print(f"Error running {algo_name}: {e}")
            self.solutionPath = [f"Error: {e}"]
            self.solutionMoves = []
            self.totalCost = 0
            self.gameState = GameState.FINISHED

    def pauseGame(self):
        if self.gameState == GameState.PLAYING:
            self.gameState = GameState.PAUSED
    
    def resetGame(self):
        self.gameState = GameState.STOPPED
        self.currentStep = 0
        self.solutionPath = []
        
        self.searchTime = 0.0
        self.nodesExpanded = 0
        self.peakMemoryKb = 0.0
        self.totalCost = 0
        
        if hasattr(self, 'originalPositions'):
            for i, (origRow, origCol) in enumerate(self.originalPositions):
                if i < len(self.vehicles):
                    # Create a new Vehicle instance with original position
                    old_vehicle = self.vehicles[i]
                    self.vehicles[i] = Vehicle(
                        old_vehicle.vehicleId,
                        origRow,  # row
                        origCol,  # col
                        old_vehicle.length,
                        old_vehicle.isHorizontal
                    )
        else:
            self.loadMap(self.currentMap)
    
    
    def update(self):
        currentTime = time.time()
        
        if self.gameState == GameState.PLAYING and self.solutionPath:
            if currentTime - self.lastMoveTime > (0.67 / self.animationSpeed):
                if self.currentStep < len(self.solutionMoves) if hasattr(self, 'solutionMoves') else 0:
                    if hasattr(self, 'solutionMoves'):
                        vid, delta = self.solutionMoves[self.currentStep]
                        
                        # Create new Vehicle instance with updated position
                        old_vehicle = self.vehicles[vid]
                        if self.vehicles[vid].isHorizontal:
                            new_row = old_vehicle.row
                            new_col = old_vehicle.col + delta
                        else:
                            new_row = old_vehicle.row + delta  
                            new_col = old_vehicle.col
                            
                        self.vehicles[vid] = Vehicle(
                            old_vehicle.vehicleId,
                            new_row,
                            new_col,
                            old_vehicle.length,
                            old_vehicle.isHorizontal
                        )
                    
                    self.currentStep += 1
                    self.lastMoveTime = currentTime
                    
                    if self.currentStep >= len(self.solutionMoves):
                        self.gameState = GameState.FINISHED
                        print("Puzzle solved! Target car reached exit.")

    def drawGrid(self):
        gridCard = pygame.Rect(
            self.gridCardX, self.gridCardY,
            self.gridCardWidth, self.gridCardHeight
        )
        pygame.draw.rect(self.screen, Colors.CARD_BG, gridCard, border_radius=12)
        
        titleY = self.gridCardY + 24
        puzzleName = self.currentMap.replace(".txt", "").replace("level", "Puzzle ")
        titleText = self.buttonFont.render(puzzleName, True, Colors.TEXT_COLOR)
        titleRect = titleText.get_rect(centerx=gridCard.centerx, y=titleY)
        self.screen.blit(titleText, titleRect)
        
        gridRect = pygame.Rect(
            self.gridX, self.gridY,
            self.gridSize * self.cellSize,
            self.gridSize * self.cellSize
        )
        pygame.draw.rect(self.screen, Colors.PANEL_BG, gridRect, border_radius=8)
        
        for i in range(1, self.gridSize):
            startPos = (self.gridX + i * self.cellSize, self.gridY)
            endPos = (self.gridX + i * self.cellSize, self.gridY + self.gridSize * self.cellSize)
            pygame.draw.line(self.screen, Colors.DARK_GRAY, startPos, endPos, 1)
            
            startPos = (self.gridX, self.gridY + i * self.cellSize)
            endPos = (self.gridX + self.gridSize * self.cellSize, self.gridY + i * self.cellSize)
            pygame.draw.line(self.screen, Colors.DARK_GRAY, startPos, endPos, 1)
        
        exitX = self.gridX + self.gridSize * self.cellSize
        exitY = self.gridY + 2 * self.cellSize
        exitHeight = self.cellSize
        
        arrowColor = Colors.ACCENT_RED
        pygame.draw.rect(self.screen, arrowColor, 
                        (exitX - 8, exitY + 5, 8, exitHeight - 10), border_radius=4)
        
        arrowPoints = [
            (exitX + 5, exitY + exitHeight // 2),
            (exitX - 2, exitY + 10),
            (exitX - 2, exitY + exitHeight - 10)
        ]
        pygame.draw.polygon(self.screen, arrowColor, arrowPoints)

    def drawCars(self):
        for vehicle in self.vehicles:
            if vehicle.isHorizontal:
                width = vehicle.length * self.cellSize - 10
                height = self.cellSize - 10
            else:
                width = self.cellSize - 10
                height = vehicle.length * self.cellSize - 10
            
            carRect = pygame.Rect(
                self.gridX + vehicle.col * self.cellSize + 5,
                self.gridY + vehicle.row * self.cellSize + 5,
                width, height
            )
            
            carImage = None
            
            if vehicle.vehicleId == 0:  # Target car
                carImage = self.targetCarImage
                fallbackColor = Colors.ACCENT_RED

            elif vehicle.length == 2:
                imageIndex = (vehicle.vehicleId - 1) % len(self.carImages)
                carImage = self.carImages[imageIndex] if imageIndex < len(self.carImages) else None
                fallbackColor = Colors.ACCENT_BLUE if vehicle.vehicleId % 3 == 1 else Colors.ACCENT_GREEN if vehicle.vehicleId % 3 == 2 else (128, 0, 128)
            elif vehicle.length == 3:
                imageIndex = (vehicle.vehicleId - 1) % len(self.truckImages)
                carImage = self.truckImages[imageIndex] if imageIndex < len(self.truckImages) else None
                fallbackColor = Colors.ACCENT_BLUE if vehicle.vehicleId % 3 == 1 else Colors.ACCENT_GREEN if vehicle.vehicleId % 3 == 2 else (128, 0, 128)
            else:
                fallbackColor = Colors.GRAY
            
            if carImage:
                if vehicle.isHorizontal:
                    scaledImage = pygame.transform.scale(carImage, (height, width))
                    scaledImage = pygame.transform.rotate(scaledImage, -90)
                else:
                    scaledImage = pygame.transform.scale(carImage, (width, height))
                
                self.screen.blit(scaledImage, carRect)
            else:
                pygame.draw.rect(self.screen, fallbackColor, carRect, border_radius=6)
                
                if vehicle.vehicleId != 0:  # Not target car
                    textColor = Colors.WHITE
                    number = str(vehicle.vehicleId)
                    text = self.smallFont.render(number, True, textColor)
                    textRect = text.get_rect(center=carRect.center)
                    self.screen.blit(text, textRect)

    def drawUI(self):
        self.screen.blit(background, (0, 0))
        headerText = self.titleFont.render("Rush Hour Solver", True, Colors.WHITE)
        headerRect = headerText.get_rect(center=(self.screenWidth // 2, 40))
        self.screen.blit(headerText, headerRect)
        
        controlCard = pygame.Rect(
            self.leftColumnX, self.leftColumnY,
            self.controlCardWidth, self.controlCardHeight
        )
        pygame.draw.rect(self.screen, Colors.CARD_BG, controlCard, border_radius=12)
        
        controlsText = self.buttonFont.render("Controls", True, Colors.WHITE)
        controlsRect = controlsText.get_rect(
            centerx=controlCard.centerx, 
            y=controlCard.top + 20
        )
        self.screen.blit(controlsText, controlsRect)
        
        metricsCard = pygame.Rect(
            self.rightColumnX, self.rightColumnY,
            self.rightColumnWidth, self.controlCardHeight
        )
        pygame.draw.rect(self.screen, Colors.CARD_BG, metricsCard, border_radius=12)
        
        metricsTitle = self.buttonFont.render("Performance Metrics", True, Colors.WHITE)
        metricsTitleRect = metricsTitle.get_rect(
            centerx=metricsCard.centerx,
            y=metricsCard.top + 20
        )
        self.screen.blit(metricsTitle, metricsTitleRect)
        
        metricsContentY = metricsCard.top + 70
        metricsContentX = metricsCard.left + 20
        
        if self.gameState == GameState.FINISHED and hasattr(self, 'searchTime'):
            if self.searchTime > 0 and hasattr(self, 'solutionMoves') and self.solutionMoves:
                metricsData = [
                    f"Algorithm: {self.currentAlgorithm.value}",
                    f"Search Time: {self.searchTime:.3f}s",
                    f"Nodes Expanded: {self.nodesExpanded}",
                    f"Peak Memory: {self.peakMemoryKb:.2f} KB"
                ]
                
                metricsData.append(f"Solution Length: {len(self.solutionMoves)} moves")
                    
                if hasattr(self, 'totalCost') and self.currentAlgorithm in [Algorithm.UCS, Algorithm.A_STAR]:
                    metricsData.append(f"Total Cost: {self.totalCost}")
                    
                for i, metric in enumerate(metricsData):
                    metricSurface = self.mediumFont.render(metric, True, Colors.WHITE)
                    self.screen.blit(metricSurface, 
                                    (metricsContentX, metricsContentY + i * 40))
                    
                if self.currentStep >= len(self.solutionMoves):
                    successCard = pygame.Rect(
                        metricsCard.left, metricsCard.bottom + 20,
                        metricsCard.width, 70
                    )
                    pygame.draw.rect(self.screen, Colors.ACCENT_GREEN, successCard, border_radius=12)
                    
                    successText = self.buttonFont.render("Puzzle Solved!", True, Colors.WHITE)
                    successRect = successText.get_rect(center=successCard.center)
                    self.screen.blit(successText, successRect)
            elif self.searchTime > 0:
                noSolutionText = self.mediumFont.render("No Solution Found", True, Colors.ACCENT_RED)
                noSolutionRect = noSolutionText.get_rect(centerx=metricsCard.centerx, y=metricsContentY + 40)
                self.screen.blit(noSolutionText, noSolutionRect)
                
                metricsData = [
                    f"Algorithm: {self.currentAlgorithm.value}",
                    f"Search Time: {self.searchTime:.3f}s",
                    f"Nodes Expanded: {self.nodesExpanded}",
                    f"Peak Memory: {self.peakMemoryKb:.2f} KB"
                ]
                
                for i, metric in enumerate(metricsData):
                    metricSurface = self.smallFont.render(metric, True, Colors.WHITE)
                    self.screen.blit(metricSurface, 
                                    (metricsContentX, metricsContentY + 80 + i * 30))
        else:
            placeholder = self.smallFont.render("Click \"Solve\" to see", True, Colors.WHITE)
            placeholder2 = self.smallFont.render("performance metrics", True, Colors.WHITE)
            
            placeholderRect = placeholder.get_rect(centerx=metricsCard.centerx, y=metricsContentY + 60)
            placeholderRect2 = placeholder2.get_rect(centerx=metricsCard.centerx, y=metricsContentY + 90)
            
            self.screen.blit(placeholder, placeholderRect)
            self.screen.blit(placeholder2, placeholderRect2)
        
        if self.solutionPath and self.gameState in [GameState.PLAYING, GameState.PAUSED]:
            statusCardHeight = 80
            statusCard = pygame.Rect(
                self.gridCardX, self.gridCardY + self.gridCardHeight + 20,
                self.gridCardWidth, statusCardHeight
            )
            pygame.draw.rect(self.screen, Colors.CARD_BG, statusCard, border_radius=12)
            
            stepText = f"Step {self.currentStep}/{len(self.solutionPath) - 1}"
            stepSurface = self.mediumFont.render(stepText, True, Colors.WHITE)
            stepRect = stepSurface.get_rect(x=statusCard.left + 20, y=statusCard.top + 15)
            self.screen.blit(stepSurface, stepRect)
            
            if 0 <= self.currentStep < len(self.solutionPath):
                action = self.solutionPath[self.currentStep]
                actionSurface = self.smallFont.render(action, True, Colors.LIGHT_GRAY)
                actionRect = actionSurface.get_rect(x=statusCard.left + 20, y=statusCard.top + 45)
                self.screen.blit(actionSurface, actionRect)
        
        for button in self.buttons:
            button.draw(self.screen)
        
        self.mapDropdown.draw(self.screen)
        
        self.algorithmDropdown.draw(self.screen)


    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                number.currentScreen = 0
                return False
            
            for button in self.buttons:
                button.handleEvent(event)
            
            for dropdown in self.dropdowns:
                dropdown.handleEvent(event)
            
            selectedAlg = self.algorithmDropdown.options[self.algorithmDropdown.selectedIndex]
            for alg in Algorithm:
                if alg.value == selectedAlg and alg != self.currentAlgorithm:
                    self.currentAlgorithm = alg
                    self.resetGame()
                    break
                    
            selectedMap = self.mapDropdown.options[self.mapDropdown.selectedIndex]
            if selectedMap != self.currentMap:
                self.currentMap = selectedMap
                self.loadMap(selectedMap)
                self.resetGame()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    number.currentScreen = 0
                    return False
        
        return True
    
    def runFrame(self):
        if not self.handleEvents():
            return False
            
        self.update()
        
        self.drawUI()      
        self.drawGrid()    
        self.drawCars()    
        
        pygame.display.flip()
        return True

