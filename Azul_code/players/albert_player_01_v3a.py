# Extened from albert_01_v2
# include score + bonus score + custome empty line score
# wins albert_player_01_v3 51% vs 46.9% 1000 runs


from advance_model import *
from utils import *
import sys
import time
import inspect
import heapq
import numpy
import random
import abc
import copy
import logging
logging.basicConfig(level=logging.DEBUG)

class myPlayer(AdvancePlayer):

    def __init__(self,_id):
        super().__init__(_id)
        self.roundnum = 0
        self.turn = 0
        self.trig_quad = 0
        if self.id == 1:
            self.opid = 0
        else:
            self.opid = 1

    def StartRound(self,game_state):
        self.roundnum += 1
        self.turn = 0
        return None

    def SelectMove(self, moves, game_state):
        #start_time = time.perf_counter()
        self.turn += 1
        
        def count_neighbour(new_move):
            count = 0
            row = 0
            column = 0
            _,_,tgrab = new_move
            move_row = tgrab.pattern_line_dest
            move_col = int(game_state.players[self.id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
            # logging.debug("count: %s and %s and %s", move_row, move_col, new_move)
            # check line is filled with the neigbour colour
        
            if move_row > 0:
                if game_state.players[self.id].lines_number[move_row] > 0 and\
                    game_state.players[self.id].lines_tile[move_row] == tgrab.tile_type:
                    count = count + (game_state.players[self.id].lines_number[move_row]/(move_row+1))

                #check if the diag tiles are filled
                if move_row + 1 <= 4 and move_col-1 >= 0 and game_state.players[self.id].grid_state[move_row+1][move_col-1] == 1:
                        count = count + 1
                if move_row + 1 <= 4 and move_col + 1 <= 4 and game_state.players[self.id].grid_state[move_row+1][move_col+1] == 1:
                        count = count + 1
                if move_col - 1 >= 0 and move_col-1 >= 0 and game_state.players[self.id].grid_state[move_row-1][move_col-1] == 1:
                        count = count + 1
                if move_col - 1 >= 0 and move_col + 1 <= 4 and game_state.players[self.id].grid_state[move_row-1][move_col+1] == 1:
                        count = count + 1

                #check if the up, down, left and right tiles are filled
                if move_row - 1 >= 0 and game_state.players[self.id].grid_state[move_row-1][move_col] == 1:
                        count = count + 1
                if move_row + 1 <= 4 and game_state.players[self.id].grid_state[move_row+1][move_col] == 1:
                        count = count + 1
                if move_col-1 >= 0 and game_state.players[self.id].grid_state[move_row][move_col-1] == 1:
                        count = count + 1
                if move_col + 1 <= 4 and  game_state.players[self.id].grid_state[move_row][move_col+1] == 1:
                        count = count + 1
            return count

        def ScoreRound(move, my_id, my_gs):
            score_inc = 0 #increase in score
            grid_state = numpy.zeros((5,5)) #for storing current move resultant tiles in the wall grid
            move_row = move[2].pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[move[2].pattern_line_dest][move[2].tile_type])

            #end of game bonus score
            rows = my_gs.players[my_id].GetCompletedRows() #past compelted row, cols, set
            cols = my_gs.players[my_id].GetCompletedColumns()
            sets = my_gs.players[my_id].GetCompletedSets()

            #calcualte num of row, cols and set compelted in current move
            row = 0
            column = 0
            current_completed_set = 0
            for i in range(5):
                row = (my_gs.players[my_id].grid_state[move_row][i]) + row
                column = (my_gs.players[my_id].grid_state[i][move_col]) + column
            if row == 4: #if 4 tiles are already filled in , fill in self, = 5,= completed
                rows = rows + 1
            if column == 4:
                cols = cols + 1
            for colour in range(5):
                if my_gs.players[my_id].number_of[colour] == 4 and move[2].tile_type == colour:
                    current_completed_set += 1

            bonus = (rows * 2) + (cols * 7) + ((sets + current_completed_set)* 10)

            return bonus #67.7% vs 29.4% 1000 runs

        scale = 5
        moves.sort(key = lambda move: ((move[2].num_to_pattern_line*scale - move[2].num_to_floor_line),\
            ScoreRound(move, self.id, game_state), count_neighbour(move)) , reverse=True) #count is important to have
        # moves.sort(key = lambda move: ((move[2].num_to_pattern_line*scale - move[2].num_to_floor_line),\
        #     ScoreRound(move, self.id, game_state)) , reverse=True) #60.2% vs 37.3% 36.72 vs 31.88
        best_move = moves[0]
        #logging.debug("albert = %s",time.perf_counter()-start_time)
        return best_move