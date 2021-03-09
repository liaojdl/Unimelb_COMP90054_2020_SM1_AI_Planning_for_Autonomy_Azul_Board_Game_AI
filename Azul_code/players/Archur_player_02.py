# This file mainly using the breath first search 
# The idea was to take each move in the quese. Each move will have a score. 
# The current node will be record as the best move and best score. When we find a 
# a higher score, it could represent a new and become a new best_move

# I feel the idea is about right. It is similar to the naive player, but it consider the score which from the 
# action. There should be some python language error. The code has some index error.
from advance_model import *
from utils import *

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)
        if self.id == 1:
            self.opid = 0
        else:
            self.opid = 1

    def StartRound(self,game_state):

        return None

    def SelectMove(self, moves, game_state):
        # Select move that involves placing the most number of tiles
        # in a pattern line. Tie break on number placed in floor line.
        # start_time = time.perf_counter()
        # max_turn_time = 0.90

        best_move = None            # Same as before, set a best_move comtains nothing
        best_score = -999           # Set a very low initial score. 
        # Breath First Search 
        def bfs(moves, game_state)
            myQueue = util.Queue()  # Try to create a Queue to store the node. 
            startState = (move, game_state)  # take a move as a startState
            myQueue.push(startState)
            visited = set()         # Set a visit array to store the visited node. to make sure 
                                    # it does not go to the same node again. 

            while not myQueue.isEmpty():
                # cur_t = time.perf_counter() - start_time
                expandStates = myQueue.pop() # Take a node from the Quese
                mid,fid,tgrab = expandStates
                # implement the current move, and get the score of the the current turn. 
                for expandStates in moves: 
                    turn_score,_ = game_state.players[self.id].ScoreRound()
                    # By comparing the score, if the score higher, it means the 
                    # current move better than the previous move. 
                    # Replace the current move as a best_move, and compare with next moves. 
                    if turn_score > best_score:
                        best_move = (mid, fid, tgrab)
                        best_score = best_score
                    return best_move


class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

