#@Anya Script to run game. Still incomplete

import os
import secrets
#import MyBot as MB
import random

def rungame():
    map_settings = {32: 400,
                    40: 425,
                    48: 450,
                    64: 500}


    #map_size = secrets.choice(list(map_settings.keys()))
    #commands =  [f'halite.exe --replay-directory replays/ -vvv --width 32 --height 32 "python MyBot.py" "python MyBot.py"']
    #os.system(commands)
    result = 0
    result += random.randint(1, 3000)
    return result