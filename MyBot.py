#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import choi_yena.hlt

# This library contains constant values.
from choi_yena.hlt import constants

# Your library
from choi_yena.utils_ import wrapper
from choi_yena.hendrick import mdp
from choi_yena.utils_ import parameters
from choi_yena.utils_ import quadrants

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging
import time
from numpy import matrix



""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = choi_yena.hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Choi Yena Bot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


ship_status = {}

ships_priority = []
retuning_queue = []


def handleShipAI(ship):
    if ship.id not in ship_status:
        ship_status[ship.id] = "exploring"

    unsafe_positions.remove(wrapper.to_tuple(ship.position))

    if ship_status[ship.id] == "returning":
        if ship.position == me.shipyard.position:
            ship_status[ship.id] = "exploring"
    elif ship.halite_amount >= parameters.maxHaliteToReturn:
        ship_status[ship.id] = "returning"
        retuning_queue.append(ship.id)
    # Decision making
    grid = None

    # Decide qual tipo de MDP usar
    if ship_status[ship.id] == "returning":
        logging.info("Returning")
        grid = wrapper.ReturnGrid(simplified_map, ship, unsafe_positions, enemy_positions, [wrapper.to_tuple(me.shipyard.position)])
    elif ship_status[ship.id] == "recalling":
        grid = wrapper.RecallGrid(simplified_map, ship, unsafe_positions, enemy_positions, [wrapper.to_tuple(me.shipyard.position)])
    else:
        grid = wrapper.VisionGrid(simplified_map,ship,unsafe_positions, enemy_positions)
        if len(grid.terminals) == 0:
            grid = wrapper.QuadrantGrid(simplified_map, quadrant_map, ship, unsafe_positions, enemy_positions)

    logging.info("Terminais: {}".format(grid.terminals))
    logging.info("Rewards: \n{}".format(grid.debug_rewards()))
    # Calcula a MDP
    result = mdp.policy_iteration(grid)

    # Analiza o resultado da MDP e retorna as informacoe usadas no jogo
    data = wrapper.parseResult(ship,game_map,grid,result)

    # Anti-Colision
    unsafe_positions.append(wrapper.to_tuple(data['new_position']))

    if data['onTerminal']:
        # Has priority
        if not data['toTerminal']:
            if ship.id in ships_priority:
                ships_priority.remove(ship.id)
    else:
        if data['toTerminal']:
            ships_priority.append(ship.id)

    # Logging area

    logging.info("Ship {} command: {} actual position: {} new position: {}".format(ship.id, data['command'], ship.position, data['new_position']))

    command_queue.append(ship.move(data['command']))

# TESTE
'''
game.update_frame()

me = game.me
game_map = game.game_map

grid = wrapper.HaliteGrid(game_map,me)

result = mdp.policy_iteration(grid)

game.end_turn([])
'''
#-------

def fetch_enemy():
    enemy_ships_ = []
    for player in game.players.values():
        if player.id != me.id:
            enemy_ships_.extend(player.get_ships())

    return enemy_ships_

def sortByPriority(item):
    if item.id in retuning_queue:
        return game_map.calculate_distance(me.shipyard.position, item.position)
    elif item.id in ships_priority:
        return 501
    else:
        return 502

count = 0

""" <<<Game Loop>>> """
while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().

    game.update_frame()

    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    simplified_map = [[row[i].halite_amount for row in game_map._cells] for i in range(len(game_map._cells[0]))]

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.

    command_queue = []

    my_ships = me.get_ships()
    enemy_ships = fetch_enemy()
    enemy_positions = [wrapper.to_tuple(enemy.position) for enemy in enemy_ships]
    

    my_ships.sort(key = sortByPriority)

    unsafe_positions = [wrapper.to_tuple(ship.position) for ship in enemy_ships + my_ships]

    quadrant_map = quadrants.quadrantGenerator(simplified_map, constants.WIDTH)

    if constants.MAX_TURNS - game.turn_number <= 30:
        for ship_id, _ in ship_status.items():
            ship_status[ship_id] = "recalling"

    # Handle ship AI
    time1 = time.time()
    for ship in my_ships:
        handleShipAI(ship)

    time2 = time.time()

    if len(my_ships) <= parameters.ship_amount + (constants.HEIGHT - 32) / 1.5 and game.turn_number < parameters.max_turn_to_spawn + (constants.MAX_TURNS - 400) / 2 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and not wrapper.to_tuple(me.shipyard.position) in unsafe_positions:
        unsafe_positions.append(wrapper.to_tuple(me.shipyard.position))
        command_queue.append(me.shipyard.spawn())

    logging.info("Time: {}".format(time2 - time1))

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)