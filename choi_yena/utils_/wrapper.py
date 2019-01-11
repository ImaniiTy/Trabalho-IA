import logging

from choi_yena import hlt
from choi_yena.hendrick.mdp import MDP
from . import parameters

commands_ = ['n','s','e','w','o']

# Completar a classe com a lista de estados, lista de rewards e a funcao T

class Cell:

     def __init__(self, x, y, has_ship, haliteAmount = 0):
         self.x = x
         self.y = y
         self.haliteAmount = haliteAmount
         self.has_ship = has_ship

class HaliteGrid(MDP):

    def __init__(self, game_map, ship, unsafe_positions):
        self.ship = ship
        self.unsafe_positions = unsafe_positions
        self.width = parameters.viewDistance * 2 + 1
        self.height = parameters.viewDistance * 2 + 1
        self.grid = self.convertMap(game_map)
        super().__init__((0, 0), actlist=commands_, terminals=self.selectTerminals(), gamma= parameters.gamma)
        self.setupStatesAndReward()

    def T(self, state, action):
        if action is None:
            return [(0,state)]
        else: 
            return [(1, self.move(state,action))]

    def convertMap(self, game_map):
        cells = []
        for y in range(self.height):
            cellsCol = []
            for x in range(self.width):
                position = hlt.positionals.Position((x - parameters.viewDistance) + self.ship.position.x, (y - parameters.viewDistance) + self.ship.position.y)
                mapCell = game_map[position]
                cellsCol.append(Cell(position.x, position.y, position in self.unsafe_positions, mapCell.halite_amount))
            cells.append(cellsCol)

        return cells

    def selectTerminals(self):
        terminals = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell.haliteAmount > parameters.maxHaliteToMove and not cell.has_ship:
                    terminals.append((y, x))

        return terminals

    def setupStatesAndReward(self):
        for y in range(self.height):
            for x in range(self.width):
                self.reward[y, x] = (self.grid[y][x].haliteAmount - parameters.maxHaliteToMove) * 10
                if not self.grid[y][x].has_ship or (x, y) == (parameters.viewDistance, parameters.viewDistance):
                    self.states.add((y, x))
                

        return

    def move(self, state, direction):
        if direction == 'n':
            resultState = (state[0] - 1, state[1])
            return resultState if resultState in self.states else state
        elif direction == 's':
            resultState = (state[0] + 1, state[1])
            return resultState if resultState in self.states else state
        elif direction == 'e':
            resultState = (state[0], state[1] + 1)
            return resultState if resultState in self.states else state
        elif direction == 'w':
            resultState = (state[0], state[1] - 1)
            return resultState if resultState in self.states else state
        elif direction == 'o':
            return state

def convert(self, values):
    return ((values[0] - parameters.viewDistance) + self.ship.position.x, (values[1] - parameters.viewDistance) + self.ship.position.y)

def parseResult(ship, game_map, mdp, mdpResult):
    tup = (parameters.viewDistance, parameters.viewDistance)

    command = mdpResult[tup] if mdpResult[tup] is not None else 'o'
    new_position = ship.position.directional_offset(convertDirection(command))

    onTerminal = tup in mdp.terminals
    toTerminal = game_map[new_position].halite_amount > parameters.maxHaliteToMove

    return {"command": command, "new_position": new_position, "onTerminal": onTerminal, "toTerminal": toTerminal}

def convertDirection(command):
    if command == hlt.commands.NORTH:
        return hlt.positionals.Direction.North
    if command == hlt.commands.SOUTH:
        return hlt.positionals.Direction.South
    if command == hlt.commands.EAST:
        return hlt.positionals.Direction.East
    if command == hlt.commands.WEST:
        return hlt.positionals.Direction.West
    if command == hlt.commands.STAY_STILL:
        return hlt.positionals.Direction.Still
    return command