# fight niaive_player = one step agent
# can be used for mcts roll out


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

    def StartRound(self,game_state):
        self.roundnum += 1
        self.turn = 0
        return None

    def SelectMove(self, moves, game_state):
        start_time = time.perf_counter()
        self.turn += 1
        best_move = moves[0]

        

        def Max_num_per_colour(i, j) :
            colour = [0, 0, 0, 0, 0]
            colour_factory_num = [0,0,0,0,0]
            for factory in game_state.factories:
                for i in range(4):
                    if factory.tiles[i] > 0:
                        colour_factory_num[i] += 1
                        colour[i] += factory.tiles[i]
            if j == 1 :
                return colour[i]
            else:
                return colour_factory_num[i]

        def tiles_in_column(my_id, my_gamestate):
            column_num = []
            grid_size = 5
            for j in range(grid_size):  #column number
                count = 0
                for i in range(grid_size):  #row
                    if my_gamestate.players[my_id].grid_state[i][j] == 1:
                        count = count + 1
                column_num.append(count)  #store in an array
            # logging.debug("column count: %s", column_num)
            return column_num

        def num_to_line_v3(column_num, moves, my_id, my_gamestate):
            move_tile_num = []
            move_colour_num = []
            move_least_factory =[]
            move_vert_num = []
            move_count_simple = []
            move_count_full_v1 = []
            move_count_full_v2 = []
            move_top_num = []
            move_rect_num = []
            move_row = []
            move_col = []
            move_empty = []
            move_index = []
            count = 0
            scale = 5
            for i in moves:
                row = i[2].pattern_line_dest
                move_col_num = int(my_gamestate.players[my_id].grid_scheme[row][i[2].tile_type])

                #array for move num_to_pattern_line
                move_tile_num.append(i[2].num_to_pattern_line*scale - i[2].num_to_floor_line)

                #array for number of tiles per colour in round
                move_colour_num.append(Max_num_per_colour(i[2].tile_type, 1))

                #array for least number of factory used to contain this move's tile colour
                move_least_factory.append(Max_num_per_colour(i[2].tile_type, 0))
                
                #array for num of tiles filled in the same vertical column
                move_vert_num.append(column_num[move_col_num])

                #array for count
                move_count_simple.append(count_neighbour_simple(i, my_id, my_gamestate))

                #array for count
                move_count_full_v1.append(count_neighbour_full_v1(i, my_id, my_gamestate))

                #array for count
                move_count_full_v2.append(count_neighbour_full_v1(i, my_id, my_gamestate)) 

                #array for row down to up rank
                move_row.append(i[2].pattern_line_dest+1)

                #array for column right to left
                move_col.append(move_col_num)
                
                #array to force fill specific area
                move_top_num.append(filter_move_v1(i))  

                #array to force fill specific area
                move_rect_num.append(filter_move_v2(i, my_id, my_gamestate)) 

                #array to calculate the empty lines
                lines_not_empty_me = 0  
                for line in my_gamestate.players[self.id].lines_number:
                    if line>0:
                        lines_not_empty_me += 1
                lines_not_empty_me = 1/(lines_not_empty_me+1)
                move_empty.append(lines_not_empty_me)
            
                #array for index
                move_index.append(count)
                count = count + 1

            # moves_sorted =  list(zip(move_tile_num, move_count_full_v2, move_index)) #61% to 35.8% 500 runs
            # moves_sorted =  list(zip(move_count_full_v2, move_tile_num, move_index)) #10 % to 88% 500 runs, doesn't work
            # moves_sorted =  list(zip(move_tile_num, move_count_full_v1, move_index)) #61.4% 37.4% 500 runs
            # moves_sorted =  list(zip(move_tile_num, move_count_full_v2, move_rect_num, move_index)) # 59%, 39% 500 runs
            # moves_sorted =  list(zip(move_tile_num, move_count_full_v2, move_top_num, move_index)) # 55.6%, 42.2% 500 runs
            # moves_sorted =  list(zip(move_tile_num, move_count_full_v2, move_empty, move_index)) # 60%, 37% 500 runs
            # moves_sorted =  list(zip(move_tile_num, move_count_simple, move_empty, move_index)) # 60.6%, 37% 500 runs
            moves_sorted =  list(zip(move_tile_num, move_count_full_v1, move_empty, move_index)) # 57.8%, 40% 500 runs
            moves_sorted.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)

            return moves[moves_sorted[0][3]]    #3 = index , index can be 1,2,3,etc
        
        def set_trig_quad(move, my_id, my_gamestate):
            #onyl run at the start
            if self.roundnum == 1 and self.turn == 1:
                #find row and column
                move_row = move[2].pattern_line_dest
                move_col = int(my_gamestate.players[my_id].grid_scheme[move[2].pattern_line_dest][move[2].tile_type])
                # self.trig_quad = [move_row, move_col]
                #sort into quadarnt, clockwise
                #quad 1: (0,1,2)(0,1,2)
                if 0 <= move_row and move_row <= 2 and 0 <= move_col and move_col <= 2:
                    self.trig_quad = 0
                #quad 2: (0,1,2)(2,3,4)
                elif 0 <= move_row and move_row <= 2 and 2 <= move_col and move_col <= 4:
                    self.trig_quad = 1
                #quad 3: (2,3,4)(2,3,4)
                elif 2 <= move_row and move_row <= 4 and 2 <= move_col and move_col <= 4 :
                     self.trig_quad = 2
                #quad 4: (2,3,4)(0,1,2)
                else :# 2 <= move_row and move_row <= 4 and 0 <= move_col and move_col <= 2
                     self.trig_quad = 3
                # logging.debug("row column: %s and %s", move_row, move_col)
                # logging.debug("quad: %s", self.trig_quad)

        def set_vertical_half(move, my_id, my_gamestate):
            #onyl run at the start
            if self.roundnum == 1 and self.turn == 1:
                move_col = int(my_gamestate.players[my_id].grid_scheme[move[2].pattern_line_dest][move[2].tile_type])
                if 0 <= move_col and move_col <= 2:
                    self.trig_quad = 0
                else :# 2 <= move_row and move_row <= 4 and 0 <= move_col and move_col <= 2
                     self.trig_quad = 1

        def filter_move_v1(move):  
            if self.roundnum == 1 and self.turn == 1:
                   return 0
            else:
                row = [0,0,1,1,1,1]
                return row[(move[2].pattern_line_dest+1)]

        def filter_move_v2(move, my_id, my_gamestate):
            #quad vertical 1
            quad_v1 = [[1,1,1,0,0],
                      [1,1,1,0,0],
                      [1,1,1,0,0],
                      [1,1,1,0,0],
                      [1,1,1,0,0]]
            
            #quad vertical 2
            quad_v2 = [[1,1,1,0,0],
                      [1,1,1,0,0],
                      [1,1,1,0,0],
                      [1,1,1,0,0],
                      [1,1,1,0,0]]
            if self.roundnum == 1 and self.turn == 1:
                   return 0
            else:
                quad2 = [quad_v1, quad_v2]
                move_row = move[2].pattern_line_dest
                move_col = int(my_gamestate.players[my_id].grid_scheme[move[2].pattern_line_dest][move[2].tile_type])
                if move_row >=  0:
                    keep = quad2[self.trig_quad][move_row][move_col]
                    return keep
                else:
                    return 0

        def count_neighbour_simple(new_move, my_id, my_gs):
            count = 0
            row = 0
            column = 0
            _,_,tgrab = new_move
            move_row = tgrab.pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
        
            if move_row > 0:
                #check if the diag tiles are filled
                if move_row + 1 <= 4 and move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row+1][move_col-1] == 1:
                        count = count + 2
                if move_row + 1 <= 4 and move_col + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col+1] == 1:
                        count = count + 2
                if move_col - 1 >= 0 and move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row-1][move_col-1] == 1:
                        count = count + 2
                if move_col - 1 >= 0 and move_col + 1 <= 4 and my_gs.players[my_id].grid_state[move_row-1][move_col+1] == 1:
                        count = count + 2

                #check if the up, down, left and right tiles are filled
                if move_row - 1 >= 0 and my_gs.players[my_id].grid_state[move_row-1][move_col] == 1:
                        count = count + 2
                if move_row + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col] == 1:
                        count = count + 2
                if move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row][move_col-1] == 1:
                        count = count + 2
                if move_col + 1 <= 4 and  my_gs.players[my_id].grid_state[move_row][move_col+1] == 1:
                        count = count + 2

            return count

        def count_neighbour_full_v2(new_move, my_id, my_gs):
            count = 0
            row = 0
            column = 0
            _,_,tgrab = new_move
            move_row = tgrab.pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
            # logging.debug("count: %s and %s and %s", move_row, move_col, new_move)
            # check line is filled with the neigbour colour
        
            if move_row > 0:
                if my_gs.players[my_id].lines_number[move_row] > 0 and\
                    my_gs.players[my_id].lines_tile[move_row] == tgrab.tile_type:
                    count = count + (my_gs.players[my_id].lines_number[move_row]/(move_row+1))

                #check if the diag tiles are filled
                if move_row + 1 <= 4 and move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row+1][move_col-1] == 1:
                        count = count + 1
                if move_row + 1 <= 4 and move_col + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col+1] == 1:
                        count = count + 1
                if move_col - 1 >= 0 and move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row-1][move_col-1] == 1:
                        count = count + 1
                if move_col - 1 >= 0 and move_col + 1 <= 4 and my_gs.players[my_id].grid_state[move_row-1][move_col+1] == 1:
                        count = count + 1

                #check if the up, down, left and right tiles are filled
                if move_row - 1 >= 0 and my_gs.players[my_id].grid_state[move_row-1][move_col] == 1:
                        count = count + 2
                if move_row + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col] == 1:
                        count = count + 2
                if move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row][move_col-1] == 1:
                        count = count + 2
                if move_col + 1 <= 4 and  my_gs.players[my_id].grid_state[move_row][move_col+1] == 1:
                        count = count + 2
                
                # #check if the row or column will be completed
                for i in range(4):
                    row = 2*(my_gs.players[my_id].grid_state[move_row][i]) + row
                    column = 2*(my_gs.players[my_id].grid_state[i][move_col]) + column
                    count = count + row + column
                if row == 4:
                    count = count + 7
                if column == 4:
                    count = count + 9

            return count

        def count_neighbour_full_v1(new_move, my_id, my_gs):
            count = 0
            row = 0
            column = 0
            _,_,tgrab = new_move
            move_row = tgrab.pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
            # logging.debug("count: %s and %s and %s", move_row, move_col, new_move)
            # check line is filled with the neigbour colour
        
            if move_row > 0:
                if my_gs.players[my_id].lines_number[move_row] > 0 and\
                    my_gs.players[my_id].lines_tile[move_row] == tgrab.tile_type:
                    count = count + 1 + (my_gs.players[my_id].lines_number[move_row]/(move_row+1))

                #check if the diag tiles are filled
                if move_row + 1 <= 4 and move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row+1][move_col-1] == 1:
                        count = count + 2
                if move_row + 1 <= 4 and move_col + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col+1] == 1:
                        count = count + 2
                if move_col - 1 >= 0 and move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row-1][move_col-1] == 1:
                        count = count + 2
                if move_col - 1 >= 0 and move_col + 1 <= 4 and my_gs.players[my_id].grid_state[move_row-1][move_col+1] == 1:
                        count = count + 2

                #check if the up, down, left and right tiles are filled
                if move_row - 1 >= 0 and my_gs.players[my_id].grid_state[move_row-1][move_col] == 1:
                        count = count + 3
                if move_row + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col] == 1:
                        count = count + 3
                if move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row][move_col-1] == 1:
                        count = count + 3
                if move_col + 1 <= 4 and  my_gs.players[my_id].grid_state[move_row][move_col+1] == 1:
                        count = count + 3
                
                # #check if the row or column will be completed
                for i in range(4):
                    row = (my_gs.players[my_id].grid_state[move_row][i]) + row
                    column = (my_gs.players[my_id].grid_state[i][move_col]) + column
                    count = count + row + column
                if row == 4:
                    count = count + 5
                if column == 4:
                    count = count + 7

            return count

        a1 = tiles_in_column(self.id, game_state)
        best_move = num_to_line_v3(a1, moves, self.id, game_state)
        set_vertical_half(best_move, self.id, game_state)
        # set_trig_quad(best_move, self.id, game_state)
        # logging.debug("albert = %s",time.perf_counter()-start_time)
        return best_move