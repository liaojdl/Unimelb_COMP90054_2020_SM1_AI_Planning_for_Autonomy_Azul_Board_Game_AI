# This file will be used in the competition
# Please make sure the following functions are well defined

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

class myPlayer(AdvancePlayer):

    def __init__(self,_id):
        super().__init__(_id)
        # sort out who is who
        if self.id is 1:
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
        max_turn_time = 0.95

        # cutting branches, sort based on descending num to pattern_line 
        # cut down to only top 10 move candidates
        def Moves_cutted(moves):
            moves_copy = copy.copy(moves)
            moves_copy.sort(key = lambda move: (move[2].num_to_pattern_line,\
            -move[2].num_to_floor_line-move[2].pattern_line_dest) , reverse=True)
            moves_copy = moves_copy[0:9]
            return moves_copy
        
        # the minimax algorithm, google it for what it is
        def minimax(gamecopy, depth, maximizingPlayer,start_t):
            cur_t = time.perf_counter()-start_t
            # this is ok
            if depth is 0 or cur_t>max_turn_time or not (gamecopy.TilesRemaining()):
                turn_score_me,_ = gamecopy.players[self.id].ScoreRound()
                turn_score_op,_ = gamecopy.players[self.opid].ScoreRound()
                score_turn_diff = turn_score_me-turn_score_op
                return score_turn_diff

            if maximizingPlayer:
                bestValue = -999
                moves_me = gamecopy.players[self.id].GetAvailableMoves(gamecopy)
                moves_me = Moves_cutted(moves_me)
                for move_me in moves_me:
                    gs_copy = copy.deepcopy(gamecopy)
                    gs_copy.ExecuteMove(self.id, move_me)
                    v = minimax(gs_copy, depth - 1, False, start_t)
                    bestValue = max(bestValue, v)
                return bestValue

            else:
                bestValue = 999 
                moves_op = gamecopy.players[self.opid].GetAvailableMoves(gamecopy)
                moves_op = Moves_cutted(moves_op)
                for move_op in moves_op:
                    gs_copy = copy.deepcopy(gamecopy)
                    gs_copy.ExecuteMove(self.opid, move_op)
                    v = minimax(gs_copy, depth - 1, True, start_t)
                    bestValue = min(bestValue, v)
                return bestValue

        best_score = -999
        moves_me1 = Moves_cutted(moves)
        # my possible move
        for move_me1 in moves_me1:
            gs_copy1 = copy.deepcopy(game_state)
            gs_copy1.ExecuteMove(self.id, move_me1)
            # maximum exploration step of 2 of minimax
            roundscore_me = minimax(gs_copy1, 2, False, start_time)
            if (roundscore_me>best_score):
                best_move = move_me1
                best_score = roundscore_me

        return best_move