# Ultimate minimax agent, with addtional weights for first player token, alpha beta prunning

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
        #count round number
        self.round_no = 0
        self.turn_no = 0
        self.roundstartmove = None
        # sort out who is who
        if self.id == 1:
            self.opid = 0
        else:
            self.opid = 1

    def StartRound(self,game_state):
        #increment round count
        self.round_no += 1
        #reset turn count
        self.turn_no = 0 
        if game_state.first_player == self.id:
            # record time to meet 1s decision timing restrictions
            start_timex = time.perf_counter()
            # time counter to be safe
            max_turn_time = 4.75
            # maximum 2 exploration steps, essentially me, op, me 3 layer minimax
            depth_int = 3
            # number of moves considered per turn
            cut_num_root = 10
            cut_num_leaves = 9
            movesx = game_state.players[self.id].GetAvailableMoves(game_state)
            best_score = -999
            moves_me1 = self.Moves_cutted(movesx, cut_num_root, self.id, game_state)
            # my possible move
            for move_me1 in moves_me1:
                gs_copy1 = copy.deepcopy(game_state)
                gs_copy1.ExecuteMove(self.id, move_me1)
                # maximum exploration step of 2 of minimax
                roundscore_me = self.minimax(gs_copy1, depth_int, -999, 999, False, start_timex, max_turn_time, cut_num_leaves)
                if (roundscore_me>best_score):
                    best_move = move_me1
                    best_score = roundscore_me
            self.roundstartmove = best_move
            #logging.debug(best_move)
            #logging.debug(time.perf_counter()-start_timex)

        return None

    # cutting branches, sort based on descending num to pattern_line
    # improved by adding num to floor line consideration
    # cut down to only top 10 move candidates
    def Moves_cutted(self, moves, cut_num, my_id, my_gs):
        moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
            -move[2].num_to_floor_line,\
            my_gs.players[my_id].lines_number[move[2].pattern_line_dest] 
            -my_gs.players[my_id].number_of[move[2].tile_type]) , reverse=True)
        moves = moves[0:cut_num]
        return moves

    # the minimax algorithm, google it for what it is
    def minimax(self, gamecopy, depth, alpha, beta, maximizingPlayer, start_t, max_t, cut_num):
        depth_int = depth
        cur_t = time.perf_counter()-start_t
        # this is ok
        if depth == 0 or cur_t>max_t or not (gamecopy.TilesRemaining()):
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
                    lines_not_empty_me += (i+1-gamecopy.players[self.id].lines_number[i])/(i+1)
            lines_not_empty_op = 0
            for i in range(len(gamecopy.players[self.opid].lines_number)):
                if gamecopy.players[self.opid].lines_number[i] >0:
                    lines_not_empty_op += (i+1-gamecopy.players[self.opid].lines_number[i])/(i+1)'''

            # Method 2: only count the number of lines not emptied, needs a higher gain 
            lines_not_empty_me = 0       
            for line in gamecopy.players[self.id].lines_number:
                if line>0:
                    lines_not_empty_me += 1
            lines_not_empty_op = 0
            for line in gamecopy.players[self.opid].lines_number:
                if line>0:
                    lines_not_empty_op += 1

            #calculate the weight for the bonus from end game score based on depth
            weight_bonus = numpy.interp(depth_int-depth, [0, 3*depth_int], [0, 1])
            weight_nonempty_lines = 1.75
            final_score_me = turn_score_me + weight_bonus * final_score_me -\
                weight_nonempty_lines*lines_not_empty_me
            final_score_op = turn_score_op + weight_bonus * final_score_op -\
                weight_nonempty_lines*lines_not_empty_op
            if gamecopy.next_first_player == self.id:
                final_score_me += 0.75
            if gamecopy.next_first_player == self.opid:
                final_score_op += 0.75
            score_turn_diff = final_score_me - final_score_op
            '''if (self.round_no<=2 and self.turn_no<=2):
                return final_score_me'''
            '''if (abs(gamecopy.players[self.id].score-gamecopy.players[self.opid].score)>20\
                and self.round_no==3):
                return final_score_me'''
            return score_turn_diff

        if maximizingPlayer:
            bestValue = -999
            moves_me = gamecopy.players[self.id].GetAvailableMoves(gamecopy)
            moves_me = self.Moves_cutted(moves_me, cut_num, self.id, gamecopy)
            for move_me in moves_me:
                gs_copy = copy.deepcopy(gamecopy)
                gs_copy.ExecuteMove(self.id, move_me)
                v = self.minimax(gs_copy, depth - 1,  alpha, beta, False, start_t, max_t, cut_num)
                bestValue = max(bestValue, v)
                alpha = max(alpha, bestValue);
                if alpha >= beta:
                    break
            return bestValue

        else:
            bestValue = 999
            moves_op = gamecopy.players[self.opid].GetAvailableMoves(gamecopy)
            moves_op = self.Moves_cutted(moves_op, cut_num, self.opid, gamecopy)
            for move_op in moves_op:
                gs_copy = copy.deepcopy(gamecopy)
                gs_copy.ExecuteMove(self.opid, move_op)
                v = self.minimax(gs_copy, depth - 1, alpha, beta, True, start_t, max_t, cut_num)
                bestValue = min(bestValue, v)
                beta = min(beta, bestValue)
                if alpha >= beta:
                    break
            return bestValue

    ## this agent considers the current step and then considers the opponent
    # the steps to give a move to maximise my score- opponent score difference
    # currently has timing problem due to not cutting branches,
    # but can maintain about 90% winrate against naive_player
    def SelectMove(self, moves, game_state):
        #logging.debug(self.roundstartmove)
        #increment turn count
        self.turn_no += 1
        # record time to meet 1s decision timing restrictions
        start_time = time.perf_counter()
        # time counter to be safe
        max_turn_time = 0.95
        # maximum 2 exploration steps, essentially me, op, me 3 layer minimax
        depth_int = 2
        # number of moves considered per turn
        cut_num_start = 10
        cut_num_leaves = 9
        best_score = -999
        if self.roundstartmove:
            #logging.debug("haha!")
            best_move = self.roundstartmove
            self.roundstartmove = None
        else:
            moves_me1 = self.Moves_cutted(moves, cut_num_start, self.id, game_state)

            # my possible move
            for move_me1 in moves_me1:
                gs_copy1 = copy.deepcopy(game_state)
                gs_copy1.ExecuteMove(self.id, move_me1)
                # maximum exploration step of 2 of minimax
                roundscore_me = self.minimax(gs_copy1, depth_int, -999, 999, False, start_time, max_turn_time, cut_num_leaves)
                if (roundscore_me>best_score):
                    best_move = move_me1
                    best_score = roundscore_me
            #logging.debug(time.perf_counter()-start_time)
        return best_move