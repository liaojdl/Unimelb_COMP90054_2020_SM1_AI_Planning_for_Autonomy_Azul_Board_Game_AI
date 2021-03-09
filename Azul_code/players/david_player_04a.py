# MCTS search advanced, a better rollout agent, pruning of actions,
# the startround 5s function is still flawed and needs to be fixed

from advance_model import *
import numpy as np
from utils import *
import time
import sys
import inspect
import heapq
import numpy
import random
import abc
import copy
from collections import defaultdict
import math

import logging
logging.basicConfig(level=logging.DEBUG)

class myPlayer(AdvancePlayer):

    def __init__(self,_id):
        super().__init__(_id)
        self.round_no = 0
        self.turn_no = 0
        # sort out who is who
        if self.id is 1:
            self.opid = 0
        else:
            self.opid = 1

    def StartRound(self,game_state):
        self.round_no += 1
        self.turn_no = 0
        '''# record time to meet 1s decision timing restrictions
        start_time = time.perf_counter()
        cur_time = time.perf_counter()-start_time
        # time counter to be safe
        max_round_time = 4.8'''
        self.root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        #root = self.root
        #root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        '''i = 0
        # if time permits do more simulations
        while (cur_time < max_round_time):
            i = i+1
            current_node = root
            # expand and select
            while not current_node.is_terminal_node():
                if not current_node.is_fully_expanded():
                    current_node = current_node.expand()
                    break
                else:
                    current_node = current_node.best_child()
            # rollout simulation
            win_or_lose = current_node.rollout()
            # backpropogate result
            current_node.backpropagate(win_or_lose)
            cur_time = time.perf_counter()-start_time
        self.root = root'''
        return None

    # try a mcts implementation
    # assuming opponent to be also quite smart too
    def SelectMove(self, moves, game_state):
        self.turn_no += 1
        # record time to meet 1s decision timing restrictions
        start_time = time.perf_counter()
        cur_time = time.perf_counter()-start_time
        # time counter to be safe
        max_turn_time = 0.95
        xx = False
        # set up mcts root
        #root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        for child in self.root.children:
            if game_state == child.game_state:
                self.root = child
                xx = True
        if xx == False:
            self.root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        root = self.root
        #root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        i = 0
        # if time permits do more simulations
        while (cur_time < max_turn_time):
            i = i+1
            current_node = root
            # expand and select
            while not current_node.is_terminal_node():
                if not current_node.is_fully_expanded():
                    current_node = current_node.expand()
                    break
                else:
                    current_node = current_node.best_child(c_param=1.0)
            # rollout simulation
            win_or_lose = current_node.rollout()
            # backpropogate result
            current_node.backpropagate(win_or_lose)
            cur_time = time.perf_counter()-start_time
        #logging.debug(i)
        # choose best child and associate next action
        best_child = root.best_child(c_param=1.0)
        best_move = best_child.action

        return best_move


# note that i still limited expansion and random rollout to only
# the most valuable 10 moves, rather than using all possible moves
class MCTS_search_node(object):

    def __init__(self, myid, opid, curplayer, action, game_state, parent=None):
        # records the id of myself and my opponent
        self.myid = myid
        self.opid = opid
        # visits and results set as float for better division
        self.n = 0.0
        self.q = 0.0
        self.scores = []
        # untried actions for the current node
        self._untried_actions = None
        # game_state
        self.game_state = game_state
        # parrent node
        self.parent = parent
        # children node
        self.children = []
        # the player to play the action to lead to a child state node
        self.curplayer = curplayer
        # the action that leads to the current state node
        self.action = action
    
    @property
    def untried_actions(self):
        if self._untried_actions is None:
            # get posssible moves of next players, cut to 12
            cut_num = 12
            moves = self.game_state.players[self.curplayer].GetAvailableMoves(self.game_state)
            moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
            -move[2].num_to_floor_line,\
            -self.game_state.players[self.curplayer].number_of[move[2].tile_type]) , reverse=True)
            moves = moves[0:cut_num]
            self._untried_actions = moves
        return self._untried_actions

    def best_child(self, c_param):
        weights = [
            ((c.q) / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(weights)]

    def expand(self):
        # random untried action
        action = self.untried_actions.pop()
        #logging.debug(action)
        # execute action
        next_state = copy.deepcopy(self.game_state)
        next_state.ExecuteMove(self.curplayer, action)
        # children expansion, remember to update the new player
        next_player = self.opid
        if self.curplayer == self.opid:
            next_player = self.myid
        child_node = MCTS_search_node(
            self.myid, self.opid, next_player, action, next_state, parent=self
        )
        #logging.debug(next_player)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return not self.game_state.TilesRemaining()

    def rollout_policy(self, moves, game_state, curplayer):
        moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
            -move[2].num_to_floor_line,\
            game_state.players[curplayer].number_of[move[2].tile_type]) , reverse=True)
        return moves[0]        
        #return random.choice(moves)

    # a random simulation of the rest of the round
    def rollout(self):
        gs_copy = copy.deepcopy(self.game_state)
        current_player = self.curplayer
        # round is running
        # try not to simulate whole round, better rather four turns
        while gs_copy.TilesRemaining():
            possible_moves = gs_copy.players[current_player].GetAvailableMoves(gs_copy)
            #action = random.choice(moves_copy)
            action = self.rollout_policy(possible_moves, gs_copy, current_player)
            gs_copy.ExecuteMove(current_player, action)
            # update the next move player
            next_player = self.opid
            if current_player == self.opid:
                next_player = self.myid
            current_player = next_player
        # Method 2: only count the number of lines not emptied, needs a higher gain 
        lines_not_empty_me = 0
        for i in range(len(gs_copy.players[self.myid].lines_number)):
            if gs_copy.players[self.myid].lines_number[i] >0:
                lines_not_empty_me += (i+1-gs_copy.players[self.myid].lines_number[i])/(i+1)
        lines_not_empty_op = 0
        for i in range(len(gs_copy.players[self.opid].lines_number)):
            if gs_copy.players[self.opid].lines_number[i] >0:
                lines_not_empty_op += (i+1-gs_copy.players[self.opid].lines_number[i])/(i+1)
        weight_nonempty_lines = 3
        # score of endofround
        myscore,_ = gs_copy.players[self.myid].ScoreRound()
        myendscore = gs_copy.players[self.myid].EndOfGameScore()
        opscore,_ = gs_copy.players[self.opid].ScoreRound()
        opendscore = gs_copy.players[self.opid].EndOfGameScore()
        weight_bonus = 0.5
        final_score_me = myscore + weight_bonus * myendscore - weight_nonempty_lines*lines_not_empty_me
        final_score_op = opscore + weight_bonus * opendscore - weight_nonempty_lines*lines_not_empty_op
        if gs_copy.next_first_player == self.myid:
            final_score_me += 0.75
        if gs_copy.next_first_player == self.opid:
            final_score_op += 0.75
        #return result
        return final_score_me-final_score_op
        #return final_score_me-final_score_op

    def backpropagate(self, result):
        self.n += 1.
        self.scores.append(result)
        self.q += result
        #self.q = sum(self.scores)/len(self.scores)
        #mean_result = sum(self.q)/len(self.q)
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0