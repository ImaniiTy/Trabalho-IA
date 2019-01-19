from choi_yena.utils_ import parameters
import math

def quadrantGenerator(origin, width):
    vD = parameters.viewDistance*2 + 1
    nQ = math.ceil(width/vD)
    quadrant = [[0 for item in range(nQ)] for row in range(nQ)]
    for x in range(nQ):
            for y in range(nQ):
                for i in range(vD):
                    for j in range(vD):
                        if(origin[(j+x*vD)%width][(i+y*vD)%width] > parameters.maxHaliteToMove):
                            quadrant[x][y] += origin[(j+x*vD)%width][(i+y*vD)%width]
    return quadrant