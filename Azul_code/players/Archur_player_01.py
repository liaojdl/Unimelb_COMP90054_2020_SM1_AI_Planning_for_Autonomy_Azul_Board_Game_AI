# Written by Michelle Blom, 2019, changed by Archur

# Actually, it is changed from the naive player.
# For the else if loop, corr_to_floor should compare with the tgrab.num_to_floor_line
# It make the new naive player has higher rate than the old version.
# Maybe david could use this new version as our rollout method for the MCTS.
# It is also a basic analysis about the Naive player about how it works. 

from advance_model import *
from utils import *

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectMove(self, moves, game_state):
        # Select move that involves placing the most number of tiles
        # in a pattern line. Tie break on number placed in floor line.
        most_to_line = -1   # In the begining, set most_to_line = -1; it represent the number could be 
                            # put on the left side blocks. 
        corr_to_floor = 0   # This variable represent the number of the titles need to place on the floor
                            

        best_move = None    # We have no best choice in th
        # In one turn, we did this for loop. 
        for mid,fid,tgrab in moves:
            if most_to_line == -1:      # In the first comparing, most to line = -1, means we did not do any move yet.
                best_move = (mid,fid,tgrab) # We take the first move from moves. 
                                            # Here, move contains: mid, fid, tgrab; moves means all the possible 
                                            #   moves in the current turn.
                # for the first possible move, most_to_line is put the same color titles on the left side block.  
                most_to_line = tgrab.num_to_pattern_line    
                # If titles is a lot, we need to put the left overs on the floor, each floor will substract points
                corr_to_floor = tgrab.num_to_floor_line
                continue
                # By now, we will treate the first move we got in the moves as a best move.

                # Comparing the current possible moves with the previous move. 
                # If the current move could put more titles on the left block, it means it could get more points
                # The current move will be the new best_move
            if tgrab.num_to_pattern_line > most_to_line:
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line
                # If the current will put the same numbers of titles on the block. We mainly compare the number of title
                # need to be placed on the floor blocks. More titles in floor means lower points. 
            elif tgrab.num_to_pattern_line == most_to_line and \
                tgrab.num_to_floor_line < corr_to_floor:
                # The only change in this code. 
                best_move = (mid,fid,tgrab)
                most_to_line = tgrab.num_to_pattern_line
                corr_to_floor = tgrab.num_to_floor_line
        return best_move
# All and all, Naive player just consider the very basic points taking. It doesn't even consider the opponent player's move.
# Follow the group's plan. I was asked to write the BFS or DFS to against the basic naive player.