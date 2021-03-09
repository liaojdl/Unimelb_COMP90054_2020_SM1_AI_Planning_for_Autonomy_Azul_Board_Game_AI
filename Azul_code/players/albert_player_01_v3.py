# Extened from albert_01_v2
# include score + bonus score + custome empty line score


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
        best_move = moves[0]
        moves_op = game_state.players[self.opid].GetAvailableMoves(game_state)

        def Max_num_per_colour(i) :
            colour = [0, 0, 0, 0, 0]
            for factory in game_state.factories:
                for i in range(4):
                    colour[i] += factory.tiles[i]
            return colour[i]

        def ken_op(tgrab, game_state):
            index = 0
            colour_total = Max_num_per_colour(tgrab.tile_type)
            tiles_left = colour_total - (tgrab.num_to_pattern_line + tgrab.num_to_floor_line)
            for line in game_state.players[self.opid].lines_number:
                if line == 0:
                    if tiles_left < index:
                        index = index + 1
                        return 1
                    else:
                        index = index + 1
                        return 0
                else:
                    return 0
        
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
            lines_not_empty_me = 0   #num of none empty lines
            weight_nonempty_lines = 1.5
            grid_state = numpy.zeros((5,5)) #for storing current move resultant tiles in the wall grid
            move_row = move[2].pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[move[2].pattern_line_dest][move[2].tile_type])
            for i in range(5): #for each line, not indcluding floor line
                if my_gs.players[my_id].lines_number[i] == i+1: #if line is filled up perfectly
                    tc = my_gs.players[my_id].lines_tile[i] #check tile colour
                    col = int(my_gs.players[my_id].grid_scheme[i][tc]) #check column num of move

                    grid_state[i][col] = 1 #update the current move to grid, here stored in temp matrix grid_state

                    # count the number of tiles in a continguous line
                    # above, below, to the left and right of the placed tile.
                    above = 0
                    for j in range(col-1, -1, -1):
                        val = grid_state[i][j] + my_gs.players[my_id].grid_state[i][j] #current(temp) + old
                        above += val
                        if val == 0:
                            break
                    below = 0
                    for j in range(col+1,5,1):
                        val = grid_state[i][j] + my_gs.players[my_id].grid_state[i][j]
                        below +=  val
                        if val == 0:
                            break
                    left = 0
                    for j in range(i-1, -1, -1):
                        val = grid_state[j][col] + my_gs.players[my_id].grid_state[j][col]
                        left += val
                        if val == 0:
                            break
                    right = 0
                    for j in range(i+1, 5, 1):
                        val = grid_state[j][col] + my_gs.players[my_id].grid_state[j][col]
                        right += val
                        if val == 0:
                            break
                    
                    # If the tile sits in a contiguous vertical line of 
                    # tiles in the grid, it is worth 1*the number of tiles
                    # in this line (including itself).
                    if above > 0 or below > 0:
                        score_inc += (1 + above + below)

                    # In addition to the vertical score, the tile is worth
                    # an additional H points where H is the length of the 
                    # horizontal contiguous line in which it sits.
                    if left > 0 or right > 0:
                        score_inc += (1 + left + right)

                    # If the tile is not next to any already placed tiles
                    # on the grid, it is worth 1 point. 
                    if above == 0 and below == 0 and left == 0 \
                        and right == 0:
                        score_inc += 1
                elif my_gs.players[my_id].lines_number[i] != 0:
                    lines_not_empty_me += 1 #penality given line not empty, our own socring metrics

            # Score penalties for tiles in floor line
            penalties = 0
            floor_num = 0
            for i in range(7):
                floor_num = my_gs.players[my_id].floor[i] + floor_num
            floor_num = move[2].num_to_floor_line + floor_num
            if floor_num >= 7 :
                floor_num = 7
            # logging.debug("floor_num = %s",floor_num)
            for i in range(floor_num):
                penalties += my_gs.players[my_id].FLOOR_SCORES[i]

            #custome scoring metics
            custom_score = weight_nonempty_lines*lines_not_empty_me

            # Players cannot be assigned a negative score in any round.
            score_change = score_inc + penalties
            if score_change < 0 and my_gs.players[my_id].score < -score_change:
                score_change = -my_gs.players[my_id].score

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
       
            # return score_change + bonus - custom_score #doesn't work well
            return score_change + bonus

        scale = 5
        moves.sort(key = lambda move: ((move[2].num_to_pattern_line*scale - move[2].num_to_floor_line),\
            ScoreRound(move, self.id, game_state), count_neighbour(move)) , reverse=True) #count is important to have
        # moves.sort(key = lambda move: ((move[2].num_to_pattern_line*scale - move[2].num_to_floor_line),\
        #     ScoreRound(move, self.id, game_state)) , reverse=True) #60.2% vs 37.3% 36.72 vs 31.88
        best_move = moves[0]
        #logging.debug("albert = %s",time.perf_counter()-start_time)
        return best_move