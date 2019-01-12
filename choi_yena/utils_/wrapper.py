import logging

from numpy import matrix
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
        self.center = (self.ship.position.x, self.ship.position.y)
        self.unsafe_positions = unsafe_positions
        self.width = self.height = parameters.viewDistance * 2 + 1
        self.ship_vision = self.constrain_map(game_map)
        super().__init__((0, 0), actlist=commands_, terminals=None, gamma=parameters.gamma)
        self.terminals = self.setup_data()

    def T(self, state, action):
        if action is None:
            return [(0,state)]
        else: 
            return [(1, self.move(state,action))]

    def constrain_map(self, map_):
        constraint = [[-10000 for _ in range(self.width)] for _ in range(self.height)]

        for i, row in enumerate(constraint):
            for j, _ in enumerate(row):
                global_position = self.to_global(i,j)
                if global_position not in self.unsafe_positions:
                    row[j] = map_[global_position[0]][global_position[1]]
        
        logging.info("\n{}".format(matrix(constraint)))
        return constraint

    def setup_data(self):
        terminals = []
        
        for i, row in enumerate(self.ship_vision):
            for j, cell in enumerate(row):
                if cell is not None:
                    if (i, j) == (parameters.viewDistance, parameters.viewDistance) and cell * 0.1 > self.ship.halite_amount:
                        self.reward[i, j] = 10000
                    else:
                        self.reward[i, j] = (cell - parameters.maxHaliteToMove) * parameters.reward_multiplier
                    self.states.add((i, j))

                    if cell > parameters.maxHaliteToMove:
                        terminals.append((i, j))
                else:
                    self.reward[i, j] = 0
        return terminals

    def move(self, state, direction):
        if direction == 'n':
            resultState = (state[0], state[1] - 1)
            return resultState if resultState in self.states else state
        elif direction == 's':
            resultState = (state[0], state[1] + 1)
            return resultState if resultState in self.states else state
        elif direction == 'e':
            resultState = (state[0] + 1, state[1])
            return resultState if resultState in self.states else state
        elif direction == 'w':
            resultState = (state[0] - 1, state[1])
            return resultState if resultState in self.states else state
        elif direction == 'o':
            return state

    def to_global(self, relative_x, relative_y):
        global_x, global_y = (relative_x - parameters.viewDistance) + self.center[0], (relative_y - parameters.viewDistance) + self.center[1]
        nomalized_x, nomalized_y = global_x % hlt.constants.HEIGHT, global_y % hlt.constants.WIDTH

        return (nomalized_x, nomalized_y)


# Utility functions
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

def to_tuple(position):
    return (position.x, position.y)