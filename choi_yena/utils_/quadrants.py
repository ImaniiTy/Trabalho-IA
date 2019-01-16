def quadrantGenerator(origin, width):
    quadrant = [[0 for item in range(4)] for row in range(4)]
    width = int(width/4)
    for x in range(4):
            for y in range(4):
                for i in range(width):
                    for j in range(width):
                        quadrant[x][y] += origin[j+x*width][i+y*width]
    return quadrant                        
    