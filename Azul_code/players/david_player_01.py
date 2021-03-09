# This file will be used in the competition
# Please make sure the following functions are well defined

from advance_model import *
from utils import *
import numpy
import random
import abc
import copy

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

    # Each player is given 1 second to select next best move
    # If exceeds 5 seconds, all your code will be terminated, 
    # a random action will be selected, and you will receive 
    # a timeout warning
    def SelectMove(self, moves, game_state):
        ## Select moves that fills up row 2 if possible every turn
        line_to_move = 1
        best_num_floor  = 7
        best_move = None
        for mid,fid,tgrab in moves:
            if line_to_move == tgrab.pattern_line_dest and \
                tgrab.num_to_floor_line < best_num_floor:
                best_move = (mid,fid,tgrab) 
                best_num_floor = tgrab.num_to_floor_line
        if best_move is None:
            for mid,fid,tgrab in moves:
                if tgrab.num_to_floor_line < best_num_floor:
                    best_move = (mid,fid,tgrab) 
                    best_num_floor = tgrab.num_to_floor_line
        return best_move
