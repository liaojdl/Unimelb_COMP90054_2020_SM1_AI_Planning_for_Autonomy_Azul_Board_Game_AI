# Extened from david_player_03a.py, uses the weighting approach of albert_03 on final score bonus
# added new weighting to punish left over tiles in a line
# Extend from david_player_03d.py
# add tie breaker from albert_player_03_tie_breaker


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
        # sort out who is who
        if self.id == 1:
            self.opid = 0
        else:
            self.opid = 1

    def StartRound(self,game_state):

        return None

    ## this agent considers the current step and then considers the opponent
    # the steps to give a move to maximise my score- opponent score difference
    # currently has timing problem due to not cutting branches,
    # but can maintain about 90% winrate against naive_player
    def SelectMove(self, moves, game_state):
        # record time to meet 1s decision timing restrictions
        start_time = time.perf_counter()
        # time counter to be safe
        max_turn_time = 0.90
        depth_int = 2
        cut_num = 10
        grid_size = 5

        # cutting branches, sort based on descending num to pattern_line
        # improved by adding num to floor line consideration
        # cut down to only top 10 move candidates
        def Moves_cutted(moves, cut_num):
            scale = 5  #to prevent 4-1 = 5-2 = 3, 5-2 is better because it used up 7 tiles
            moves.sort(key = lambda move: (move[2].num_to_pattern_line*scale - move[2].num_to_floor_line) , reverse=True)
            #moves.sort(key = lambda move: (move[2].num_to_pattern_line*scale + game_state.players[self.id].number_of[move[2].tile_type] - move[2].num_to_floor_line) , reverse=True)
            moves = moves[0:cut_num]
            return moves

        def count_neighbour(new_move, my_id, my_gs):
            count = 0
            row = 0
            column = 0
            _,_,tgrab = new_move
            move_row = tgrab.pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
            # logging.debug("count: %s and %s and %s", move_row, move_col, new_move)
            # check line is filled with the neigbour colour
        
            if move_row > 0:
                # if my_gs.players[my_id].lines_number[move_row] > 0 and\
                #     my_gs.players[my_id].lines_tile[move_row] == tgrab.tile_type:
                #     count = count + (my_gs.players[my_id].lines_number[move_row]/(move_row+1))

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
                        count = count + 1
                if move_row + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col] == 1:
                        count = count + 1
                if move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row][move_col-1] == 1:
                        count = count + 1
                if move_col + 1 <= 4 and  my_gs.players[my_id].grid_state[move_row][move_col+1] == 1:
                        count = count + 1
                
                # #check if the row or column will be completed
                # for i in range(4):
                #     row = my_gs.players[my_id].grid_state[move_row][i] + row
                #     column = my_gs.players[my_id].grid_state[i][move_col] + column
                #     count = count + row + column
                # if row == 4:
                #     count = count + 1
                # if column == 4:
                #     count = count + 1

            return count

        def tie_select(tie_move, new_move, my_id, my_gs, old_col, old_row):
            row_count = 0
            column_count = 0
            _,_,tgrab = new_move
            if tgrab.pattern_line_dest > 0 :
                move_row = tgrab.pattern_line_dest
                move_col = int(my_gs.players[my_id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
                for i in range(grid_size):
                    if my_gs.players[my_id].grid_state[move_row][i] == 1:
                        row_count = row_count + 1
                    if my_gs.players[my_id].grid_state[i][move_col] == 1:
                        column_count = column_count + 1
            else:
                row_count = 0
                column_count = 0

            a = [(column_count, row_count, 1),(old_col, old_row, 0)]
            a.sort(key = lambda x: (x[1],x[0]), reverse=True)
            if a[0][2] == 1:
                return [new_move, column_count, row_count]
            else:
                return [tie_move, old_col, old_row]

        def count_neighbour_v2(new_move, my_id, my_gs):
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
                        count = count + 2
                if move_row + 1 <= 4 and my_gs.players[my_id].grid_state[move_row+1][move_col] == 1:
                        count = count + 2
                if move_col-1 >= 0 and my_gs.players[my_id].grid_state[move_row][move_col-1] == 1:
                        count = count + 2
                if move_col + 1 <= 4 and  my_gs.players[my_id].grid_state[move_row][move_col+1] == 1:
                        count = count + 2
                
                #check if the row or column will be completed
                for i in range(4):
                    row = my_gs.players[my_id].grid_state[move_row][i] + row
                    column = my_gs.players[my_id].grid_state[i][move_col] + column
                    count = count + row + column
                if row == 4:
                    count = count + 1
                if column == 4:
                    count = count + 1

            return count

        def tie_select_v2(tie_move, new_move, my_id, my_gs, old_count):
            count = count_neighbour(new_move, my_id, my_gs)
            if count > old_count:
                # logging.debug("count: %s and %s = %s", count, old_count, count)
                return [new_move, count]
            else:
                # logging.debug("count: %s and %s = %s", count, old_count, old_count)
                return [tie_move, old_count]

        # the minimax algorithm, google it for what it is
        def minimax(gamecopy, depth, maximizingPlayer,start_t):
            cur_t = time.perf_counter()-start_t
            # this is ok
            if depth == 0 or cur_t>max_turn_time or not (gamecopy.TilesRemaining()):
                turn_score_me,_ = gamecopy.players[self.id].ScoreRound()
                turn_score_op,_ = gamecopy.players[self.opid].ScoreRound()
                final_score_me = gamecopy.players[self.id].EndOfGameScore()
                final_score_op = gamecopy.players[self.opid].EndOfGameScore()

                # METHOD 1: count number of left tiles, score is size_pattern_line-left_tiles,
                # if there are 2 tiles left in 5th row, then loses 3 points
                # very similar performance, needs more tuning
                '''lines_not_empty_me = 0
                for i in range(len(gamecopy.players[self.id].lines_number)):
                    if gamecopy.players[self.id].lines_number[i] >0:
                        lines_not_empty_me += (i+1-gamecopy.players[self.id].lines_number[i])/i+1
                lines_not_empty_op = 0
                for i in range(len(gamecopy.players[self.opid].lines_number)):
                    if gamecopy.players[self.opid].lines_number[i] >0:
                        lines_not_empty_op += (i+1-gamecopy.players[self.opid].lines_number[i])/i+1'''

                # Method 2: only count the number of lines not emptied, needs a higher gain 
                lines_not_empty_me = 0       
                for line in gamecopy.players[self.id].lines_number:
                    if line>0:
                        lines_not_empty_me += 1
                lines_not_empty_op = 0
                for line in gamecopy.players[self.opid].lines_number:
                    if line>0:
                        lines_not_empty_op += 1
                #logging.debug("%d,%d",lines_not_empty_me,lines_not_empty_op)
                #calculate the weight for the bonus from end game score based on depth
                weight_bonus = numpy.interp(depth_int-depth, [0, 3*depth_int], [0, 1])
                weight_nonempty_lines = 1.75
                #weight_nonempty_lines = numpy.interp(depth+1, [0, 3*depth_int], [0, 1])
                final_score_me = turn_score_me + weight_bonus * final_score_me - weight_nonempty_lines*lines_not_empty_me
                final_score_op = turn_score_op + weight_bonus * final_score_op - weight_nonempty_lines*lines_not_empty_op
                score_turn_diff = final_score_me - final_score_op
                # score_turn_diff = turn_score_me - turn_score_op
                return score_turn_diff

            if maximizingPlayer:
                bestValue = -999
                moves_me = gamecopy.players[self.id].GetAvailableMoves(gamecopy)
                moves_me = Moves_cutted(moves_me, cut_num)
                for move_me in moves_me:
                    gs_copy = copy.deepcopy(gamecopy)
                    gs_copy.ExecuteMove(self.id, move_me)
                    v = minimax(gs_copy, depth - 1, False, start_t)
                    bestValue = max(bestValue, v)
                return bestValue

            else:
                bestValue = 999
                moves_op = gamecopy.players[self.opid].GetAvailableMoves(gamecopy)
                moves_op = Moves_cutted(moves_op, cut_num)
                for move_op in moves_op:
                    gs_copy = copy.deepcopy(gamecopy)
                    gs_copy.ExecuteMove(self.opid, move_op)
                    v = minimax(gs_copy, depth - 1, True, start_t)
                    bestValue = min(bestValue, v)
                return bestValue

        best_score = -999
        moves_me1 = Moves_cutted(moves, cut_num)
        old_col = 0
        old_row = 0
        old_count = 0
        # my possible move
        for move_me1 in moves_me1:
            old_row_count = 0
            old_column_count = 0

            gs_copy1 = copy.deepcopy(game_state)
            gs_copy1.ExecuteMove(self.id, move_me1)

            # maximum exploration step of 2 of minimax
            roundscore_me = minimax(gs_copy1, depth_int, False, start_time)
            if roundscore_me > best_score:
                best_score = roundscore_me
                best_move = move_me1
                old_count = count_neighbour(best_move, self.id, gs_copy1)
                # logging.debug("break")
            elif roundscore_me == best_score: #always record tie for highest score
                # update move by comparing metric, metrics used  = column and row filled tiles total
                # tie = tie_select(best_move, move_me1, self.id, gs_copy1, old_col, old_row)
                # best_move, old_col, old_row = tie
                best_move, old_count = tie_select_v2(best_move, move_me1, self.id, gs_copy1, old_count)

        return best_move