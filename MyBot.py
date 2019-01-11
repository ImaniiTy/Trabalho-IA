#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import choi_yena.hlt

# This library contains constant values.
from choi_yena.hlt import constants

# This library contains direction metadata to better interface with the game.
from choi_yena.hlt.positionals import Direction
from choi_yena.hlt.positionals import Position
# This library allows you to generate random numbers.
import random

# Your library
from choi_yena.utils_ import wrapper
from choi_yena.hendrick import mdp
from choi_yena.utils_ import parameters

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging
import time

'''
def shipView(viewDistance, shipNeighborhoods):
    for j in range(-1 * viewDistance, viewDistance + 1):
        for i in range(-1 * viewDistance, viewDistance + 1):
            shipNeighborhoods.append((i, j))

def shipViewRelative(viewDistance, shipNeighborhoodRelative):
    for j in range(-1 * viewDistance, viewDistance + 1):
        for i in range(-1 * viewDistance, viewDistance + 1):
            shipNeighborhoodRelative.append(ship.position + Position(i, j))

shipNeighborhood = []
shipNeighborhoodRelative = []
shipView(3, shipNeighborhood)

positionActions = shipNeighborhood

shipNeighborhoodRelative = []
shipViewRelative(3, shipNeighborhoodRelative)
positionOptions = shipNeighborhoodRelative
positionDict = {}
haliteDict = {}

#logging.info(f"{positionOptions}")
#logging.info(f"{positionActions}")
for n, direction in enumerate(positionActions):
    positionDict[direction] = positionOptions[n]



for direction in positionDict:
    position = positionDict[direction]
    haliteInPosition = game_map[position].halite_amount
    haliteDict[direction] = haliteInPosition

logging.info(f"{positionDict}")
logging.info(f"{haliteDict}")
'''

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

ships_collecting = []

def handleShipAI(ship):
    logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))

    if ship.id not in ship_status:
        ship_status[ship.id] = "exploring"
    
    if ship_status[ship.id] == "returning":
        if ship.position == me.shipyard.position:
            ship_status[ship.id] = "exploring"
        else:
            move = game_map.naive_navigate(ship, me.shipyard.position)
            command_queue.append(ship.move(move))
            return
    elif ship.halite_amount >= parameters.maxHaliteToReturn:
        ship_status[ship.id] = "returning"
    
    # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
    #   Else, collect halite.

    grid = wrapper.HaliteGrid(game_map,ship,unsafe_positions)
    result = mdp.policy_iteration(grid)

    logging.info("\nResultado: {}".format(result))

    direction = wrapper.getBestChoice(game_map[ship.position],result)
    if direction == 'o':
        ships_collecting.append(ship.id)
    else:
        if ship.id in ships_collecting:
            ships_collecting.remove(ship.id)

    unsafe_positions.append(ship.position.directional_offset(wrapper.convertDirection(direction)))
    command_queue.append(ship.move(direction))

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

def sortByPriority(item):
    return item.id not in ships_collecting

count = 0

""" <<<Game Loop>>> """
while True:
    '''
    count += 1
    if count == 200:
        logging.info("sleep")
        time.sleep(2)
    '''
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().

    game.update_frame()

    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map



    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    unsafe_positions = []

    #logging.info(sorted(result.keys(), key=lambda x: x[1]))

    ships = me.get_ships()
    ships.sort(key= sortByPriority)

    for ship in ships:
        handleShipAI(ship)

    '''
    while len(ships_collecting) > 0:
        id = ships_collecting.pop()
        if me.has_ship(id):
            handleShipAI(me.get_ship(id))
            #ships.remove(me.get_ship(id))
    
    while len(ships) > 0:
        handleShipAI(ships.pop())
    '''
    logging.info([(p.x, p.y) for p in unsafe_positions])
    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
