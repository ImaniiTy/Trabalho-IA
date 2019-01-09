import hlt
import logging

from hendrick.mdp import MDP
from . import parameters

commands = ['n','s','e','w','o']

# Completar a classe com a lista de estados, lista de rewards e a funcao T

class Cell:

     def __init__(self, ship, haliteAmount = 0,):
         self.haliteAmount = haliteAmount
         self.ship = ship


class HaliteGrid(MDP):

    def __init__(self, game_map, me):
        self.grid = self.convertMap(game_map)
        self.width = game_map.width
        self.height = game_map.height
        super().__init__(self, (0, 0), actlist=commands, terminals=self.selectTerminals(), gamma= parameters.gamma)

    def convertMap(self, game_map):
        cells = []
        for x in range(game_map.width):
            cellsCol = []
            for y in range(game_map.height):
                position = hlt.positionals.Position(x,y)
                mapCell = game_map[position]
                cellsCol.append(Cell(mapCell.ship is not None, mapCell.halite_amount))
            cells.append(cellsCol)

        return cells

    def selectTerminals(self):
        terminals = []
        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y]
                if cell.haliteAmount > parameters.maxHaliteToMove and not cell.ship:
                    terminals.append((x,y))

        return terminals

                
                
        