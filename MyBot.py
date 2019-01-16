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



""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = choi_yena.hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


ship_status = {}

ships_priority = []

def handleShipAI(ship):
    if ship.id not in ship_status:
        ship_status[ship.id] = "exploring"

    unsafe_positions.remove(wrapper.to_tuple(ship.position))
    # Decision making
        
    grid = wrapper.VisionGrid(simplified_map,ship,unsafe_positions)
    #modificado
    result = mdp.policy_iteration(grid)

    data = wrapper.parseResult(ship,game_map,grid,result)

    if ship_status[ship.id] == "returning":
        if ship.position == me.shipyard.position:
            ship_status[ship.id] = "exploring"
        else:
            move = game_map.naive_navigate(ship, me.shipyard.position)
            data['new_position'] = ship.position.directional_offset(move)
            data['command'] = choi_yena.hlt.positionals.Direction.convert(move)
    elif ship.halite_amount >= parameters.maxHaliteToReturn:
        ship_status[ship.id] = "returning"

    # Anti-Colision
    unsafe_positions.append(wrapper.to_tuple(data['new_position']))
    game_map[data['new_position']].mark_unsafe(ship)

    if data['onTerminal']:
        # Has priority
        if not data['toTerminal']:
            if ship.id in ships_priority:
                ships_priority.remove(ship.id)
    else:
        if data['toTerminal']:
            ships_priority.append(ship.id)

    # Logging area
    #logging.info("\n\nResult: {}".format(result))
    logging.info("Ship {} command: {} actual position: {} new position: {}".format(ship.id, data['command'], ship.position, data['new_position']))
    logging.info(unsafe_positions)

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
    return item.id not in ships_priority

count = 0

""" <<<Game Loop>>> """
while True:

    count += 1
    if count == 200:
        logging.info("sleep")
        time.sleep(2)

    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().

    game.update_frame()

    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    simplified_map = [[row[i].halite_amount for row in game_map._cells] for i in range(len(game_map._cells[0]))]
    #quadrant = quadrants.quadrantGenerator(simplified_map, constants.WIDTH)
    #logging.info(np.matrix(simplified_map))



    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.

    command_queue = []

    my_ships = me.get_ships()
    enemy_ships = fetch_enemy()

    my_ships.sort(key = sortByPriority)

    unsafe_positions = [wrapper.to_tuple(ship.position) for ship in enemy_ships + my_ships]

    # Remover quando fizer o codigo de retorno
    for ship in enemy_ships + my_ships:
        game_map[ship.position].mark_unsafe(ship)
    #---------------------------------

    # Handle ship AI
    for ship in my_ships:
        handleShipAI(ship)

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)