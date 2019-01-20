import logging

from numpy import matrix
from choi_yena import hlt
from choi_yena.hendrick.mdp import MDP
from . import parameters

commands_ = ['n','s','e','w','o']

# Completar a classe com a lista de estados, lista de rewards e a funcao T

class HaliteGrid(MDP):

    def __init__(self, game_map, ship, unsafe_positions, enemy_positions):
        self.ship = ship
        self.center = (self.ship.position.x, self.ship.position.y)
        self.unsafe_positions = unsafe_positions
        self.width = self.height = parameters.viewDistance * 2 + 1
        self.map_size = len(game_map)
        self.ship_vision = self.constrain_map(game_map)
        self.enemy_positions = enemy_positions
        super().__init__((parameters.viewDistance, parameters.viewDistance), actlist=commands_, terminals=[], gamma=parameters.gamma)

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
                row[j] = map_[global_position[0]][global_position[1]]

        return constraint

    def setup_data(self):  
        raise NotImplementedError

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

    def tuple_to_global(self, relative):
        return self.to_global(relative[0], relative[1])
    
    def get_distance(self, from_, to):
        return abs(from_[0] - to[0]) + abs(from_[1] - to[1])

    def debug_rewards(self):
        rewards = []
        for i, row in enumerate(self.ship_vision):
            rewards_row = []
            for j, _ in enumerate(row):
                rewards_row.append(self.reward[i, j])
            
            rewards.append(rewards_row)

        return rewards
class VisionGrid(HaliteGrid):

    def __init__(self, game_map, ship, unsafe_positions, enemy_positions):
        super().__init__(game_map, ship, unsafe_positions, enemy_positions)
        self.setup_data()

    def setup_data(self):
        for i, row in enumerate(self.ship_vision):
            for j, cell in enumerate(row):
                if (i, j) == (parameters.viewDistance, parameters.viewDistance) and int(cell * 0.1) > self.ship.halite_amount:
                    self.reward[i, j] = parameters.objective_reward
                elif self.to_global(i, j) in self.unsafe_positions:
                    self.reward[i, j] = parameters.death_penality * parameters.enemy_multiplier if self.to_global(i, j) in self.enemy_positions else parameters.death_penality
                else:
                    self.reward[i, j] = (cell - parameters.maxHaliteToMove) * parameters.reward_multiplier
                self.states.add((i, j))

                if cell > parameters.maxHaliteToMove:
                    self.reward[i, j] *= parameters.terminal_multiplier
                    self.terminals.append((i, j))
class QuadrantGrid(HaliteGrid):
    
    def __init__(self, game_map, quadrant_map, ship, unsafe_positions, enemy_positions):
        super().__init__(game_map,ship,unsafe_positions, enemy_positions)
        self.quadrant_map = quadrant_map
        self.my_location = (int(self.center[0] / len(quadrant_map)), int(self.center[1] / len(quadrant_map)))
        self.setup_data()

    def setup_data(self):
        objective = self.set_direction()
        logging.info("Objective: {}".format(objective))
        for i, row in enumerate(self.ship_vision):
            for j, cell in enumerate(row):
                if (i, j) == objective or ((i, j) == (parameters.viewDistance, parameters.viewDistance) and int(cell * 0.1) > self.ship.halite_amount):
                    self.reward[i, j] = parameters.objective_reward
                elif self.to_global(i, j) in self.unsafe_positions:
                    self.reward[i, j] = parameters.death_penality * parameters.enemy_multiplier if self.to_global(i, j) in self.enemy_positions else parameters.death_penality
                else:
                    self.reward[i, j] = cell * -parameters.reward_multiplier
                self.states.add((i, j))

        self.terminals.append(objective)
    
    def set_direction(self):
        edges = self.get_edges()
        closest_quadrant = self.get_closest()
        global_closest_quadrant = self.quadrant_to_global(closest_quadrant)

        smallest_distance_edge = edges[0]
        for edge in edges:
            global_edge = self.to_global(edge[0], edge[1])
            global_smallest_distance_edge = self.to_global(smallest_distance_edge[0], smallest_distance_edge[1])
            if self.get_distance(global_edge, global_closest_quadrant) < self.get_distance(global_smallest_distance_edge, global_closest_quadrant):
                smallest_distance_edge = edge
        
        return smallest_distance_edge
    
    def get_closest(self):
        closest_quadrant = (0, 0)
        for i, row in enumerate(self.quadrant_map):
            for j, cell in enumerate(row):
                if cell > 0 and (i, j) != self.my_location:
                    closest_quadrant = (i, j) if self.get_distance(self.my_location, (i, j)) < self.get_distance(self.my_location, closest_quadrant) else closest_quadrant
        
        return closest_quadrant

    def get_edges(self):
        edges = []
        for i in range(len(self.ship_vision)):
            edges.append((0,i))
            edges.append((len(self.ship_vision) - 1,i))
            edges.append((i,0))
            edges.append((i,len(self.ship_vision) - 1))

        return edges

    def quadrant_to_global(self, quadrant):
        return ((quadrant[0] * len(self.quadrant_map) + parameters.viewDistance) % self.map_size, (quadrant[1] * len(self.quadrant_map) + parameters.viewDistance) % self.map_size)

class ReturnGrid(HaliteGrid):
    def __init__(self, game_map, ship, unsafe_positions, enemy_positions, drop_location):
        self.drop_location = drop_location
        super().__init__(game_map, ship, unsafe_positions, enemy_positions)
        self.setup_data()

    def setup_data(self):
        objective = self.get_objective()
        logging.info("Unsafe: {}".format(self.unsafe_positions))
        for i, row in enumerate(self.ship_vision):
            for j, cell in enumerate(row):
                if self.to_global(i, j) in self.unsafe_positions:
                    self.reward[i, j] = parameters.death_penality * parameters.enemy_multiplier if self.to_global(i, j) in self.enemy_positions else parameters.death_penality
                elif (i, j) == objective:
                    self.reward[i, j] = parameters.objective_reward
                else:
                    self.reward[i, j] = cell * -parameters.reward_multiplier
                self.states.add((i, j))

        self.terminals.append(objective)

    def get_objective(self):
        objective = (0, 0)
        for i, row in enumerate(self.ship_vision):
            for j, _ in enumerate(row):
                if self.get_distance(self.to_global(i, j), self.drop_location) < self.get_distance(self.tuple_to_global(objective), self.drop_location):
                    objective = (i, j)
        
        return objective


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