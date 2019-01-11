def shipView(viewDistance, shipNeighborhoods):
    for j in range(-1 * viewDistance, viewDistance + 1):
        for i in range(-1 * viewDistance, viewDistance + 1):
            shipNeighborhoods.append((i, j))

def shipViewRelative(viewDistance, shipNeighborhoodRelative):
    for j in range(-1 * viewDistance, viewDistance + 1):
        for i in range(-1 * viewDistance, viewDistance + 1):
            shipNeighborhoodRelative.append(ship.position + Position(i, j))

def mappingShipView():
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