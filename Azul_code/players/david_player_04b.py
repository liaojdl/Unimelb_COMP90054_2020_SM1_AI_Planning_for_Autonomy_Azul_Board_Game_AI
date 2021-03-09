# This file will be used in the competition
# Please make sure the following functions are well defined

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
        # sort out who is who
        if self.id is 1:
            self.opid = 0
        else:
            self.opid = 1

    def StartRound(self,game_state):
        # record time to meet 1s decision timing restrictions
        start_time = time.perf_counter()
        cur_time = time.perf_counter()-start_time
        # time counter to be safe
        max_round_time = 4.8
        self.root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        '''root = self.root
        i = 0
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
                    current_node = current_node.best_child(c_param=1.414)
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
        # record time to meet 1s decision timing restrictions
        start_time = time.perf_counter()
        cur_time = time.perf_counter()-start_time
        # time counter to be safe
        max_turn_time = 0.95

        # set up mcts root
        #root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        xx = False
        #logging.debug(BoardToString(self.root.game_state))
        if True:
            #check if state is already in the tree, if yes no need to rebuild tree
            for child in self.root.children:
                # assume same factories setup
                comp1 = True
                for i in range(5):
                    if child.game_state.factories[i].tiles != game_state.factories[i].tiles:
                        comp1 = False
                comp2 = child.game_state.centre_pool.tiles == game_state.centre_pool.tiles
                if comp1 and comp2:
                    self.root = child
                    xx = True
            if xx == False:
                #logging.debug("!")
                self.root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        root = self.root
        #root = MCTS_search_node(self.id, self.opid, self.id, None, game_state, None)
        i = 0
        # if time permits do more simulations
        while (cur_time<max_turn_time) :
            i = i+1
            current_node = root
            # expand and select
            while not current_node.is_terminal_node():
                if not current_node.is_fully_expanded():
                    current_node = current_node.expand()
                    break
                else:
                    current_node = current_node.best_child(c_param=1.414)
            # rollout simulation
            win_or_lose = current_node.rollout()
            # backpropogate result
            current_node.backpropagate(win_or_lose)
            cur_time = time.perf_counter()-start_time
        #logging.debug(i)
        # choose best child and associate next action
        best_child = root.best_child(c_param=1.414)
        self.root = best_child
        best_move = best_child.action
        #logging.debug(time.perf_counter()-start_time)
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
            cut_num = 9
            # get posssible moves of next players, cut to 20
            moves = self.game_state.players[self.curplayer].GetAvailableMoves(self.game_state)
            moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
             -move[2].num_to_floor_line-move[2].pattern_line_dest) , reverse=True)
            moves = moves[0:cut_num]
            self._untried_actions = moves
        return self._untried_actions


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

    def rollout_policy(self, moves):
        moves.sort(key = lambda move: (move[2].num_to_pattern_line,\
             -move[2].num_to_floor_line-move[2].pattern_line_dest) , reverse=True)
        best_move = moves[0]

        return best_move        
        #return random.choice(moves)

    # a random simulation of the rest of the round
    def rollout(self):
        gs_copy = copy.deepcopy(self.game_state)
        current_player = self.curplayer
        # round is running
        # try not to simulate whole round, better rather four turns
        depth = 99
        depth_int = 3
        while gs_copy.TilesRemaining() and depth>0:
            possible_moves = gs_copy.players[current_player].GetAvailableMoves(gs_copy)
            action = self.rollout_policy(possible_moves)
            gs_copy.ExecuteMove(current_player, action)
            # update the next move player
            next_player = self.opid
            if current_player == self.opid:
                next_player = self.myid
            current_player = next_player
            depth -= 1
        # Method 2: only count the number of lines not emptied, needs a higher gain 
        lines_not_empty_me = 0       
        for line in gs_copy.players[self.myid].lines_number:
            if line>0:
                lines_not_empty_me += 1
        lines_not_empty_op = 0
        for line in gs_copy.players[self.opid].lines_number:
            if line>0:
                lines_not_empty_op += 1
        weight_nonempty_lines = 1.75
        # score of endofround
        myscore,_ = gs_copy.players[self.myid].ScoreRound()
        myendscore = gs_copy.players[self.myid].EndOfGameScore()
        opscore,_ = gs_copy.players[self.opid].ScoreRound()
        opendscore = gs_copy.players[self.opid].EndOfGameScore()
        weight_bonus = 0.33
        #weight_bonus = numpy.interp(depth_int-depth, [0, 3*depth_int], [0, 1])
        final_score_me = myscore + weight_bonus * myendscore - weight_nonempty_lines*lines_not_empty_me
        final_score_op = opscore + weight_bonus * opendscore - weight_nonempty_lines*lines_not_empty_op
        
        #return result
        return final_score_me-final_score_op

    def backpropagate(self, result):
        self.n += 1.
        self.q += 0.8*result
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param):
        weights = [
            (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(weights)]