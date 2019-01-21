#@Anya Script to run game. Still incomplete
import sys, os
#sys.path.append(os.path.abspath(os.path.join('..', '../../utils_')))
import secrets
import random

def rungame():
    map_settings = {32: 400,
                    40: 425,
                    48: 450,
                    64: 500}


    map_size = secrets.choice(list(map_settings.keys()))
    commands =  'halite.exe --replay-directory replays/ -vvv --width 32 --height 32 "python MyBotN.py" "python MyBotN.py"'
    x = os.system(commands)