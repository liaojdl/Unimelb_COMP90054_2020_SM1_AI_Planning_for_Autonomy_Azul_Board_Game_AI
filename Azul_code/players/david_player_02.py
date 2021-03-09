# This file will be used in the competition
# Please make sure the following functions are well defined

from advance_model import *
from utils import *
import numpy
import random
import abc
import copy
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class myPlayer(AdvancePlayer):

    def __init__(self,_id):
        super().__init__(_id)

    def StartRound(self,game_state):
        return None

      
    def SelectMove(self, moves, game_state):
        ## Select moves that maximises per turn score return
        start_time = time.perf_counter()
        best_turn_score = -999
        best_move = None
        cut_num = 10

        def Moves_cutted(moves, cut_num):
            scale = 5  #to prevent 4-1 = 5-2 = 3, 5-2 is better because it used up 7 tiles
            moves.sort(key = lambda move: (move[2].num_to_pattern_line*scale - move[2].num_to_floor_line) , reverse=True)
            moves = moves[0:cut_num]
            return moves

        moves_me1 = Moves_cutted(moves, cut_num)
        for move in moves_me1:
            # copy for prediction
            gs_copy = copy.deepcopy(game_state)
            gs_copy.ExecuteMove(self.id,move)
            turn_score,_ = gs_copy.players[self.id].ScoreRound()
            if turn_score > best_turn_score:
                best_move = move
                best_turn_score = turn_score
        logging.debug(time.perf_counter()-start_time)
        return best_move