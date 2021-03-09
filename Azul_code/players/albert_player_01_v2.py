#extend from albert_player_01, made cleaner and stuff


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
        start_time = time.perf_counter()
        self.turn += 1
        best_move = moves[0]
        moves_op = game_state.players[self.opid].GetAvailableMoves(game_state)

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
                return 1/(colour_factory_num[i]+1)
        
        # def Max_num_per_colour(i) :
        #     colour = [0, 0, 0, 0, 0]
        #     for factory in game_state.factories:
        #         for i in range(4):
        #             colour[i] += factory.tiles[i]
        #     return colour[i]

        #find the empty lines in the op, 
        #for move colour, the remaining colour unused will not fit perfectly in op empty line
        #return score for that move 
        def ken_op(tgrab, game_state):
            index = 0
            colour_total = Max_num_per_colour(tgrab.tile_type, 1)
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

        def count_neighbour_v1(new_move, my_id, my_gs):
            count = 0
            row = 0
            column = 0
            _,_,tgrab = new_move
            move_row = tgrab.pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
        
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

                #check if the row or column will be completed
                for i in range(4):
                    row = (my_gs.players[my_id].grid_state[move_row][i]) + row
                    column = (my_gs.players[my_id].grid_state[i][move_col]) + column
                    count = count + row + column
                if row == 4:
                    count = count + 7
                if column == 4:
                    count = count + 9

            return count

        def num_to_line_v1(moves, my_id, my_gamestate):
            move_tile_num = []
            move_colour_num = []
            move_row = []
            move_col = []
            move_least_factory = []
            move_count_simple = []
            move_count_v1 =[]
            move_ken = []
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

                #array for row down to up rank
                move_row.append(i[2].pattern_line_dest+1)

                #array for column right to left
                move_col.append(move_col_num)

                #array for count
                move_count_simple.append(count_neighbour_simple(i, my_id, my_gamestate))

                #array for count
                move_count_v1.append(count_neighbour_v1(i, my_id, my_gamestate))

                #array for least number of factory used to contain this move's tile colour
                move_least_factory.append(Max_num_per_colour(i[2].tile_type, 0))

                #array for ken op
                move_ken.append(ken_op(i[2],my_gamestate))

                #array for index
                move_index.append(count)
                count = count + 1

            # moves_sorted =  list(zip(move_colour_num, move_least_factory, move_row, move_index))
            # moves_sorted =  list(zip(move_colour_num, move_least_factory, move_tile_num, move_row, move_index))
            moves_sorted =  list(zip(move_tile_num, move_count_v1, move_index))
            moves_sorted.sort(key=lambda x: (x[0], x[1]), reverse=True)
            return moves[moves_sorted[0][2]]    #2 = index , index can be 1,2,3,etc

        def num_to_line_v2(moves, my_id, my_gamestate):
            move_tile_num = []
            move_colour_num = []
            move_row = []
            move_col = []
            move_index = []
            move_least_factory = []
            move_count_simple = []
            move_count_v1 =[]
            move_ken = []
            count = 0
            scale = 5
            for i in moves:
                row = i[2].pattern_line_dest
                move_col_num = int(my_gamestate.players[my_id].grid_scheme[row][i[2].tile_type])

                #array for move num_to_pattern_line
                move_tile_num.append(i[2].num_to_pattern_line*scale - i[2].num_to_floor_line)

                #array for number of tiles per colour in round
                move_colour_num.append(Max_num_per_colour(i[2].tile_type, 1))

                #array for row down to up rank
                move_row.append(i[2].pattern_line_dest+1)

                #array for count
                move_count_simple.append(count_neighbour_simple(i, my_id, my_gamestate))

                #array for count
                move_count_v1.append(count_neighbour_v1(i, my_id, my_gamestate))

                #array for least number of factory used to contain this move's tile colour
                move_least_factory.append(Max_num_per_colour(i[2].tile_type, 0))

                #array for column right to left
                move_col.append(move_col_num)

                #array for ken op
                move_ken.append(ken_op(i[2],my_gamestate))
            
                #array for index
                move_index.append(count)
                count = count + 1

            moves_sorted =  list(zip(move_tile_num, move_least_factory, move_count_v1, move_index)) #60.8&% 37.61 vs 37% 1000 runs
            # moves_sorted =  list(zip(move_colour_num, move_least_factory, move_tile_num, move_col, move_index)) #61.0&% 38.4 at 1000 runs
            # moves_sorted =  list(zip(move_tile_num, move_count_v1, move_index)) #61.8&% at 100 runs
            moves_sorted.sort(key=lambda x: (x[0],x[1],x[2]), reverse=True)
            return moves[moves_sorted[0][3]]    #2 = index

        if self.roundnum == 1 or self.roundnum == 2:
            best_move = num_to_line_v2(moves,self.id, game_state)
        else:
            best_move = num_to_line_v2(moves,self.id, game_state)
        # logging.debug("albert = %s",time.perf_counter()-start_time)

        return best_move