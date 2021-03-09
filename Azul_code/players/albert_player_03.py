# This file will be used in the competitio
# Please make sure the following functions are well definedn
# Extened from david_player_03a.py

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
        max_turn_time = 0.95
        depth_int = 2
        cut_num = 10
        # cutting branches, sort based on descending num to pattern_line
        # cut down to only top 10 move candidates
        def Moves_cutted(moves, cut_num):
            moves_copy = copy.deepcopy(moves)
            moves_copy.sort(key = lambda move: move[2].num_to_pattern_line, reverse=True)
            moves_copy = moves_copy[0:cut_num]
            return moves_copy

        # the minimax algorithm, google it for what it is
        def minimax(gamecopy, depth, maximizingPlayer,start_t):
            cur_t = time.perf_counter()-start_t
            # this is ok
            if depth == 0 or cur_t>max_turn_time or not (gamecopy.TilesRemaining()):
                # if cur_t>max_turn_time :
                #     logging.debug("time: %s, depth %s", cur_t, depth)
                turn_score_me,_ = gamecopy.players[self.id].ScoreRound()
                turn_score_op,_ = gamecopy.players[self.opid].ScoreRound()
                final_score_me = gamecopy.players[self.id].EndOfGameScore()
                final_score_op = gamecopy.players[self.opid].EndOfGameScore()
                #calculate the weight for the bonus from end game score based on depth
                weight = numpy.interp(depth, [0, depth_int], [0, 1])
                weight = (1 - weight)
                # logging.debug("weight: %s, depth %s", weight, depth)
                final_score_me = turn_score_me + weight * final_score_me
                final_score_op = turn_score_op + weight * final_score_op
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

        # my possible move
        for move_me1 in moves_me1:
            gs_copy1 = copy.deepcopy(game_state)
            gs_copy1.ExecuteMove(self.id, move_me1)
            # maximum exploration step of 2 of minimax
            roundscore_me = minimax(gs_copy1, depth_int, False, start_time)
            #roundscore_me,_ = gs_copy1.players[self.id].ScoreRound()
            if (roundscore_me>best_score):
                best_move = move_me1
                best_score = roundscore_me

        return best_move