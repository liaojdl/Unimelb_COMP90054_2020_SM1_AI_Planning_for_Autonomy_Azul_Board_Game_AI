# This file will be used in the competition
# Please make sure the following functions are well defined

from advance_model import *
from utils import *
import numpy
import random
import abc
import copy

# instead of using end-of-round score, now
# considers end-of-game score
# apparently performance worsened
class myPlayer(AdvancePlayer):

    def __init__(self,_id):
        super().__init__(_id)

    def StartRound(self,game_state):
        return None

    def SelectMove(self, moves, game_state):
        ## Select moves that maximises per turn score return
        best_end_score = -999
        best_move = None
        for move in moves:
            # copy for prediction
            gs_copy = copy.deepcopy(game_state)
            gs_copy.ExecuteMove(self.id,move)
            turn_score,_ = gs_copy.players[self.id].ScoreRound()
            end_score = turn_score+gs_copy.players[self.id].EndOfGameScore()
            if end_score > best_end_score:
                best_move = move
                best_end_score = turn_score
        return best_move