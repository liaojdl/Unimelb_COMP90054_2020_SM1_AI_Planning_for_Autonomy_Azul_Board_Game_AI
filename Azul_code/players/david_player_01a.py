# This file will be used in the competition
# Please make sure the following functions are well defined

from advance_model import *
from utils import *
import numpy
import random
import abc
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class myPlayer(AdvancePlayer):

    # initialize
    # The following function should not be changed at all
    def __init__(self,_id):
        super().__init__(_id)
    # Each player is given 5 seconds when a new round started
    # If exceeds 5 seconds, all your code will be terminated and 
    # you will receive a timeout warning
    def StartRound(self,game_state):
        return None

    def SelectMove(self, moves, game_state):
        #start_time = time.perf_counter()
        # Select move that involves placing the most number of tiles
        # in a pattern line. Tie break on number placed in floor line.
        moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
             -move[2].num_to_floor_line-move[2].pattern_line_dest) , reverse=True)
        best_move = moves[0]
        #logging.debug(time.perf_counter()-start_time)
        return best_move