from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.a_star import AStarFinder


class Robot(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        
        self.pos = pos # robot coordenates
        self.numberBoxesStack = 0 # no. of boxes that are been carried by the robot       
        self.selfMovents = 0 # no. of movements that this robot is making
        self.pickedBoxes = 0 # no. of picked boxes since the start of the simulation individualy
        self.auxIndex = 0 # Auxilar index to handle the positions traversed in our path to an empty closest stack tile. 
        self.allocatedStack = 0 # Assigned Stack tile where the robot most get the picked boxes
        self.tileType = "Robot"
        self.empty = True # attribute that help to leave boxes in a stack tile
        self.leavedBoxes = False # attribute for APIs purposes



    def step(self):

        # Usamos los vecinos de la posición actual considerando las diagonales
        next_moves = self.model.grid.get_neighborhood(self.pos, moore=True)
        # Seleccionamos alguno de los vecinos de forma aleatoria y nos movemos a él
        next_move = self.random.choice(next_moves)


        # checamos si está lleno el stack del robot actual
        print("en stack del robot actual: ", self.numberBoxesStack)
        if self.numberBoxesStack == 5:
            isfullStack = True
        else:
            isfullStack = False
        

        if not isfullStack:
            print("no estoy lleno")
            self.leavedBoxes = False 
            isClean = self.pickAction()
            print("clean: ", isClean)
            
            if self.selfMovents >= self.model.time:
                print("Time's over, total movents: ", self.selfMovents * self.model.robots)
            if(self.model.boxNo == 0 and self.isAllRobotsEmpty()):
                print("All boxes have been picked up, adding up to: ", self.getTotalMovements(), " of total movents")
            if( self.selfMovents < self.model.time and isClean ):
                self.selfMovents += 1
                self.model.grid.move_agent(self, next_move)
        else:
            print("estoy lleno")

            pathToStack = self.getPathToClosestTileStack(self.allocatedStack)
            print("path: ",pathToStack, "len: ", len(pathToStack), "auxIndex: ", self.auxIndex)
            if( self.auxIndex < len(pathToStack) ):
                next_move = pathToStack[self.auxIndex]
                self.auxIndex = 1
                self.model.grid.move_agent(self, next_move)
            else:
                self.auxIndex = 0
                self.numberBoxesStack = 0
                print("dejo cajas xd")
                self.leaveBoxes()
                self.leavedBoxes = True
                self.assignNewStack()
            
            isClean = True



    def pickAction(self):
        listTiles = self.model.grid.get_cell_list_contents([self.pos])

        for tile in listTiles:

            if self.model.boxNo == 0:
                if self.numberBoxesStack == 0:
                    self.empty = True
                    return False
                elif self.numberBoxesStack != 0:
                    self.createArrayOfNonFullStack()
                    self.goToEmptyTileStack()

            if (tile.tileType == "Box"):

                tile.clean = True
                tile.assignStackPosX = self.allocatedStack[0]
                tile.assignStackPosY = self.allocatedStack[1]
                tile.changeColor()
                self.pickedBoxes += 1
                self.numberBoxesStack += 1
                tile.inStack = self.numberBoxesStack
                print("Bloques recogidos: ", self.numberBoxesStack)
                self.model.boxNo -= 1
                print("bloques restantes: ", self.model.boxNo)
                return False
            else:
                return True
    
    def getTotalMovements(self):
        movs = 0
        for robot in self.model.robsArray:
            movs += robot.selfMovents
        return movs

    def isAllRobotsEmpty(self):
        for robot in self.model.robsArray:
            if robot.empty == False:
                return False
        return True
    

    def leaveBoxes(self):
        listTiles = self.model.grid.get_cell_list_contents([self.pos])
        for tile in listTiles:
            if( tile.tileType == "Stack"):
                tile.boxesInTile = 5
                self.numberBoxesStack = 0
                self.auxIndex = 0

    def assignNewStack(self):
        if( len( self.model.stacksPos ) > 0 ):
            stackIndex = self.random.randint(0, len( self.model.stacksPos ) - 1)
            tupleOfStack = self.model.stacksPos[stackIndex]

            self.allocatedStack = tupleOfStack
            del self.model.stacksPos[stackIndex]

    
     #funcion auxiliar que saca la ruta hacia el stack mas cercano
    def getPathToClosestTileStack(self, path):
      grid = PathGrid(matrix=self.model.matrix)
      #print(self.model.matrix)
      grid.cleanup()
      start = grid.node(self.pos[0],self.pos[1])
      print("start x:", self.pos[0]," y: ", self.pos[1])
      end = grid.node(self.allocatedStack[0],self.allocatedStack[1])
      print("end x:", self.allocatedStack[0]," y: ", self.allocatedStack[1])
      finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
      path, runs = finder.find_path(start, end, grid)
      return path
        

    def getPathToEmptyTileStack(self, stack):

        print(self.model.matrix)
        grid.cleanup()
        
        start = grid.node( self.pos[0], self.pos[1] )
        end = grid.node( stack.pos[0], stack.pos[1] )
        finder = AStarFinder( diagonal_movement=DiagonalMovement.never )
        path, runs = finder.find_path(start, end, grid)
        return path

    def createArrayOfNonFullStack(self):
        indexAux = 0
        for stack in self.model.arrStacks:
            if stack.full:
                del self.model.arrStacks[indexAux]
            indexAux += 1

        for stack in self.model.arrStacks:
            print("Stacks without been filled yet: ", stack.boxes, " pos: ", stack.pos)

    def goToEmptyTileStack(self):
        if ( len(self.model.arrStacks) > 0 ):
            path = self.getPathToEmptyTileStack(self.model.arrStacks[0])
            if( self.auxIndex < len( path ) ):
                next_move = path[self.auxIndex]
                self.auxIndex += 1
                self.model.grid.move_agent(self, next_move)
            else:
                self.auxIndex = 0
                self.leaveMissingBoxes()
    
    def leaveMissingBoxes(self):
        listTiles = self.model.grid.get_cell_list_contents([self.pos])

        for tile in listTiles:
            if( tile.tileType == "Stack" ) :
                if( tile.boxes < 5 ):
                    if( ( tile.boxes + self.numberBoxesStack ) < 5 ):
                        tile.boxes = tile.boxes + self.numberBoxesStack
                        self.empty = True
                        self.numberBoxesStack = 0
                    elif ( ( tile.boxes + self.numberBoxesStack ) == 5  ):
                        tile.boxes = 5
                        self.numberBoxesStack = 0
                        tile.full = True
                    else:
                        spareBoxes = ( tile.boxes + self.numberBoxesStack ) - 5
                        tile.boxes = 5
                        tile.full = True
                        self.numberBoxesStack = spareBoxes
                else:
                    print("shouldn't get here")

# Usamos esta clase para crear las celdas sucias (las identificamos como agentes sin movimiento) 
class Box(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.tileType = "Box"
        self.pos = pos
        self.assignStackPosX = -1
        self.assignStackPosY = -1
        self.inStack = -1
        self.clean = False

    def changeColor(self):
        self.tileType = "stdTile"


class stdTile(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.clean = True
        self.tileType = "stdTile"


class Stack(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.boxes = 0
        self.full = False
        self.tileType = "Stack"
        

class Floor(Model):
    #se asignan las variables modificables por el usuario siendo filas, columnas, robots, tiempo de ejecucion y el numero de bloques sucios
    def __init__(self, rows =10,columns = 10, robotsNo = 1, time = 20000, boxNo = 60):
        super().__init__()

        self.schedule = RandomActivation(self)

        self.rows = rows
        self.columns = columns
        self.robotsNo = robotsNo
        self.time = time
        self.boxNo = boxNo
        self.Stacks = (boxNo // 5)
  

        self.grid = MultiGrid(self.columns, self.rows, torus=False)

        self.matrix = []
        self.stacksPos = []
        self.arrStacks = []
        self.robsArray = []
        #se crea una matriz de ceros para identificar las casillas sucias y limpias
        self.createZeroMatrix()
        #se crean los robots y bloques tanto limpios como sucios para colocarse en el tablero
        self.setStacks()
        self.setRobot()
        self.setBox()
        self.setStdTile()

    def step(self):
        self.schedule.step()
    
    @staticmethod
    def count_type(model):
        return model.boxNo
    
    def createZeroMatrix(self):
        for i in range(0, self.rows):
            zeros = []
            for j in range(0, self.columns):
                zeros.append(0)
            self.matrix.append(zeros)

    def setBox(self):
        tiles = self.boxNo
        while tiles > 0:
            randomPosX = self.random.randint(0, self.rows - 1)
            randomPosY = self.random.randint(0, self.columns - 1)
            while self.matrix[randomPosX][randomPosY] == 1:
                randomPosX = self.random.randint(0, self.rows - 1)
                randomPosY = self.random.randint(0, self.columns - 1)
            tile = Box( self, (randomPosY, randomPosX) )
            self.grid.place_agent( tile, tile.pos )
            self.matrix[randomPosX][randomPosY] = 1
            tiles -= 1
            self.schedule.add(tile)
    
    def setStdTile(self):
        for _, x, y in self.grid.coord_iter():
            if self.matrix[y][x] == 0:
                tile = stdTile( self, (x,y) )
                self.grid.place_agent(tile, tile.pos)
    
    def setRobot(self):
        for _ in range(0, self.robotsNo):
            rob = Robot(self,(1,1))

            if( len(self.stacksPos) > 0 ):
                stackIndex = self.random.randint( 0, len(self.stacksPos) - 1)
                stackTuple = self.stacksPos[stackIndex]
                rob.allocatedStack = stackTuple
                del self.stacksPos[stackIndex]

            self.robsArray.append(rob)
            self.grid.place_agent(rob, rob.pos)
            self.schedule.add(rob)



    def setStacks(self):
        for _ in range(0,self.Stacks):
            randomPosX = self.random.randint(0, (self.rows) -1)
            randomPosY = self.random.randint(0, (self.columns) -1)

            while self.matrix[randomPosX][randomPosY] == 1:
                randomPosX = self.random.randint(0, (self.rows) -1)
                randomPosY = self.random.randint(0, (self.columns) -1)
            
            stack = Stack(self, ( randomPosY, randomPosX ))
            self.grid.place_agent( stack, stack.pos )
            self.matrix[randomPosX][randomPosY] = 1
            
            self.stacksPos.append(stack.pos)
            self.arrStacks.append(stack)
            self.schedule.add(stack)
    
def agent_portrayal(agent):
    if( agent.tileType == "Robot" ):
        return {"Shape": "walle.png", "Layer": 0}
    elif( agent.tileType == "Box" ):
        return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "brown", "Layer": 1}
    elif( agent.tileType == "stdTile"):
        return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "#ced4da", "Layer": 1}
    elif( agent.tileType == "Stack" ):
        if agent.boxes == 5:
            agent.full = True
            return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "green", "Layer": 1}
        return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "red", "Layer": 1}
    
grid = CanvasGrid( agent_portrayal, 10, 10, 450, 450 )

server = ModularServer( Floor, [grid], "Store", {} )
server.port = 8524
server.launch()