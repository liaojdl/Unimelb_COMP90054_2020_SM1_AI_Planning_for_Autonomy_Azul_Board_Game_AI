# This file will be used in the competition
# Please make sure the following functions are well defined

from advance_model import *
from utils import *
import numpy
import copy
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
        start_time = time.perf_counter()
        x = game_state.players[self.id].grid_state
        def sum_neighbour(i,j,grid):
            sumx = 0
            if i>0:
                sumx += grid[i-1][j]
                if j>0:
                    sumx += grid[i-1][j-1]
            if i<4:
                sumx += grid[i+1][j]
                if j<4:
                    sumx += grid[i+1][j+1]
            if j>0:
                sumx += grid[i][j-1]
                if i<4:
                    sumx += grid[i+1][j-1]
            if j<4:
                sumx += grid[i][j+1]
                if i>0:
                    sumx += grid[i-1][j+1]
            return sumx

        def density_sum(grid):
            den_sum = 0
            for i in range(5):
                for j in range(5):
                    if grid[i][j] == 1:
                        den_sum += sum_neighbour(i,j,grid)
            return den_sum

        def togrid(tile_type,line_dest,grid):
            gridx = copy.copy(grid)
            col = tile_type+line_dest
            if col>4:
                col = col-5
            gridx[line_dest,col] = 1
            return gridx

        # Select move that involves placing the most number of tiles
        # in a pattern line. Tie break on number placed in floor line.
        moves.sort(key = lambda move: (\
            density_sum(togrid(move[2].tile_type, move[2].pattern_line_dest,\
            game_state.players[self.id].grid_state)),\
            move[2].num_to_pattern_line*5-move[2].num_to_floor_line) , reverse=True)
        '''moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
             -move[2].num_to_floor_line-move[2].pattern_line_dest) , reverse=True)'''
        #moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
        #     -move[2].num_to_floor_line-move[2].pattern_line_dest) , reverse=True)
        best_move = moves[0]
        #logging.debug(time.perf_counter()-start_time)
        return best_move