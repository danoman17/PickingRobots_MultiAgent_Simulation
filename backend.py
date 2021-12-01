import flask
from flask.json import jsonify
import uuid
import robots2
from robots2 import Floor

games = {}

app = flask.Flask(__name__)

@app.route("/mesa", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    games[id] = Floor() # instanseando el juego con la clase de Model
    print("id: ", id)
    return "ok", 201, {'Location': f"/mesa/{id}"}


@app.route("/mesa/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    listaRobots = []

    for i in range( len( model.schedule.agents ) ):
        agent = model.schedule.agents[i]

        if type(agent) is robots2.Robot:
            listaRobots.append({"x":agent.pos[0], "y": agent.pos[1], "tipo":"Robot","cajasActualesRobot":agent.numberBoxesStack, "leavedBoxes":agent.leavedBoxes })
        elif type(agent) is robots2.Box:
            listaRobots.append({"x":agent.pos[0], "y": agent.pos[1], "tipo":"Caja", "limpio": agent.clean, "stackAsignadoX":agent.assignStackPosX, "stackAsignadoY":agent.assignStackPosY, "inStack":agent.inStack})
        elif type(agent) is robots2.Stack:
            listaRobots.append({"x":agent.pos[0], "y": agent.pos[1], "tipo":"Stack", "boxesInStack": agent.boxes})
        else:
            i = i - 1
    return jsonify({"Items": listaRobots})

app.run()