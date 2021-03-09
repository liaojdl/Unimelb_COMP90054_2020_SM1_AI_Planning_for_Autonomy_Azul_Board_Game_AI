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

        # cutting branches, sort based on descending num to pattern_line
        # improved by adding num to floor line consideration
        # cut down to only top 10 move candidates
        def Moves_cutted(moves, cut_num):
            scale = 5  #to prevent 4-1 = 5-2 = 3, 5-2 is better because it used up 7 tiles
            moves.sort(key = lambda move: (move[2].num_to_pattern_line*scale - move[2].num_to_floor_line) , reverse=True)
            #moves.sort(key = lambda move: (move[2].num_to_pattern_line*scale + game_state.players[self.id].number_of[move[2].tile_type] - move[2].num_to_floor_line) , reverse=True)
            moves = moves[0:cut_num]
            return moves

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
                weight_nonempty_lines = 1.5
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

        tie_count = 0
        best_move_list = []
        last_visit = 0
        # my possible move

        for move_me1 in moves_me1:
            gs_copy1 = copy.deepcopy(game_state)
            gs_copy1.ExecuteMove(self.id, move_me1)
            # maximum exploration step of 2 of minimax
            roundscore_me = minimax(gs_copy1, depth_int, False, start_time)
            if (roundscore_me>best_score):
                last_visit = 0
                best_move = move_me1
                best_score = roundscore_me
            elif (roundscore_me == best_score): #always record tie for highest score
                last_visit = 1
                if tie_count > 0 and roundscore_me > best_move_list[0][0] : #start again if score is higher
                    best_move_list.clear()
                    tie_count = 0
                    best_move_list.append((roundscore_me, best_move))
                    best_move_list.append((roundscore_me, move_me1))
                    #bug here
                tie_count = tie_count + 1
                # logging.debug("tie_count: %s", tie_count)
                
        # logging.debug("list: %s", best_move_list)
        if tie_count > 0 and last_visit == 1:
            index_num = 0
            count_array = []
            cur_t = time.perf_counter()-start_time
            for x in best_move_list :
                _,move = x
                _,_,tgrab = move
                grid_size = 5
                column_count = 0  
                row_count = 0 
                move_row = tgrab.pattern_line_dest
                move_col = int(gs_copy1.players[self.id].grid_scheme[tgrab.pattern_line_dest][tgrab.tile_type])
                for i in range(grid_size):
                    if gs_copy1.players[self.id].grid_state[move_row][i] == 1:
                        row_count = row_count + 1
                    if gs_copy1.players[self.id].grid_state[i][move_col] == 1:
                        column_count = column_count + 1
                
                # logging.debug("index_num: %s", index_num)
                count_array.append((row_count,column_count , index_num))
                # count_array.append((column_count, row_count, index_num))
                index_num = index_num + 1
                count_array.sort(key = lambda x: (x[0],x[1]), reverse=True)

            # logging.debug("count_array: %s", count_array)
            i = count_array[0][2] #first element index
            # logging.debug("i: %s", i)
            best_move = best_move_list[i][1]
            # logging.debug("yes %s", best_move)

        return best_move