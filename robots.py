import random
import time

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import TextElement
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter


class Robot(Agent):
    def __init__(self, model, pos, stackBoxes):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.stackBoxes = stackBoxes

    def step(self):
        # Usamos los vecinos de la posición actual considerando las diagonales
        next_moves = self.model.grid.get_neighborhood(self.pos, moore=True)
        # Seleccionamos alguno de los vecinos de forma aleatoria y nos movemos a él
        next_move = self.random.choice(next_moves)

        # Se guarda la lista de los agentes que se encuentran en la posición a la que se quiere dirigir el robot
        # Esta lista puede contener un agente DirtyTile y/o 1 o más agentes Robots
        angentsList = self.model.grid.get_cell_list_contents(next_move)

        # Iteramos por cada agente
        for agent in angentsList:
            # Si dicho agente es una celda sucia, la limpiamos removiendo el dicho agente
            if(str(type(agent).__name__) == "Box"):
                self.model.grid.remove_agent(agent)
                
                # También disminuimos el total de celdas con basura en el grid
                self.model.trashAmount -= 1

                self.stackBoxes += 1;
                break
        
        if self.stackBoxes >= 5:
            print("terminó un robot, debes de dejar las cajas")
            self.stackBoxes = 0

        # Movemos el robot a su nueva posición
        self.model.grid.move_agent(self, next_move)

        # Aumentamos el total de movimientos de los robots
        self.model.totalMovimientos += 1
        

# Usamos esta clase para crear las celdas sucias (las identificamos como agentes sin movimiento) 
class Box(Agent):
     def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos

class Floor(Model):
    # Declaramos estos como atributos de la clase para poder usarlos en las demás clases que 
    # tengan acceso al modelo
    totalTime = 0
    percentageClean = 0
    trashAmount = 0
    totalMovimientos = 0

    def __init__(self, x=50, y=50, numRobots=10, trashPercentage=50, maxTime=60):
        super().__init__()
        self.schedule = RandomActivation(self)

        self.x = x
        self.y = y

        # Usamos un MultiGrid para poder colocar múltiples agentes en una misma celda
        self.grid = MultiGrid(x, y, torus=False)

        # Declaramos nuestras variables que ingresará el usuario desde el input
        self.startTime = 0
        self.maxTime = maxTime

        # Cuando el counter haya aumentado (es decir, después de la primera llamada al constructor)
        # se pueden pedir los datos de porcentaje de basura, número de Robots y duración máxima
        self.startTime = time.time()
        
        # Calculamos el total de basura que se debe insertar en la matriz 
        trashTotal = int((x*y) * (trashPercentage/100))

        # Lo declaramos como global y vacío por si en otras llamadas al constructor se habían incrementado sus elementos 
        self.trashAmount = 0

        # Reiniciamos el conteo de movimientos en cada llamada al constructor
        self.totalMovimientos = 0

        # Creamos una lista con números aleatorios en el rango de la basura que desea el usuario
        randomNumsList = random.sample(range(x*y), trashTotal)

        # Insertamos la basura iterativamente en posiciones aleatorias
        for i in randomNumsList:
          posY = i//x
          posX = i%x
          # llamamos a la clase DirtyTile y la instanciamos con las coordenadas de la matriz declarada.
          boxTile = Box(self, (posX, posY))
          # Aumentamos la cantidad de basura en el grid
          self.trashAmount += 1
          # enviamos como parametro a la clase place_agent para que se muestre en el navegador
          self.grid.place_agent(boxTile, boxTile.pos)
          
        #Inicializacion de clase Robot para la entrada de n modelos
        for _ in range(numRobots):
          gh = Robot(self, (1, 1))
          self.grid.place_agent(gh, gh.pos)
          self.schedule.add(gh)

    def step(self):
        self.schedule.step()

        # Si el tiempo actual sobrepasa el tiempo en el que debe terminar la simulación, se detiene la simulación
        if(self.startTime + self.maxTime < time.time() or self.trashAmount == 0):
            self.running = False
            
            # Calculamos el tiempo que duró la simulación
            self.totalTime = round(time.time() - self.startTime)

            # Calculamos el porcentage de celdas limpias en el grid
            totalCeldas = self.x*self.y
            self.percentageClean = round(((totalCeldas-self.trashAmount)/totalCeldas) * 100, 2)

# creamos la clase de TextResults, la cual nos devuelve una serie de etiquetas de texto con los resultados obtenidos durante y al final de la simulación. 
# haciendo uso de HTML podemos colocar las etiquetas en nuestra aplicación con ayuda de etiquetas como <br> y <hr> para tener una mejor organización. 
class TextResults(TextElement):
    def render(self, model):
        return f"""
            <br>Tiempo necesario hasta que todas las celdas estén limpias (o se haya llegado al tiempo máximo): <b>{model.totalTime} segundos </b>
            <hr>
            Porcentaje de celdas limpias después del termino de la simulación: <b>{model.percentageClean}% </b>
            <hr>
            Número de movimientos realizados por todos los agentes: <b>{model.totalMovimientos} movimientos</b>
        """

def agent_portrayal(agent):
    # si el tipo de clase recibido es DirtyTile, retornamos un muro
    if str(type(agent).__name__) == "DirtyTile":
         return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Gray", "Layer": 0}
    # sino retornamos una imagen
    return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Blue", "Layer": 0}

# Establecemos el tamaño del CanvasGrid que sea de 50*50 celdas
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

# Hacemos uso de la funcion de UserSettableParameter, la cual nos da una serie de widgets que nos permiten tener una mejor interacción con la simulación a traves de sliders, inputs de texto, entre otros, lo que nos permite manipuilar facilmente los valores iniciales.
server = ModularServer(Floor, [grid, TextResults()], "PacMan", {
  
    # Leemos el dato y con ayuda de un Slider
    "y": UserSettableParameter('slider', 'Número de filas', value=50, min_value=2, max_value=50, step=1),

    # Leemos el dato x con ayuda de un Slider
    "x": UserSettableParameter('slider', 'Número de columnas', value=50, min_value=2, max_value=50, step=1),

    # A traves de un drop down box para ingresar el total de robots.
    "numRobots": UserSettableParameter("number", "Número de robots", value=10), 

    # A traves de un drop down box para ingresar el porcentaje de basura.
    "trashPercentage": UserSettableParameter("number", "Porcentaje de basura (Formato: 50 -> 50%)", value=50),

    # A traves de un drop down box para ingresar el la duracion máxima.
    "maxTime": UserSettableParameter("number", "Duración máxima de la simulación (segundos)", value=60),
})
server.port = 8573
server.launch()