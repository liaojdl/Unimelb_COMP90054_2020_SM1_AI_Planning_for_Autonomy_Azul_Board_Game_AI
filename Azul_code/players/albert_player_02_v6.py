# Written by Albert 2020
from advance_model import *
from utils import *
import logging  #get ride of later
logging.basicConfig(level=logging.DEBUG)


class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)
        if self.id == 1:
            self.opid = 0
        else:
            self.opid = 1

    def SelectMove(self, moves, game_state):
        start_time = time.perf_counter()
        best_move = None
        best_score_kid = -999
        worst_score_kid_op = 999
        max_turn_time = 0.90
        new_move = []
        count = 0

        def ScoreRound(move, my_id, my_gs):
            score_inc = 0 #increase in score
            lines_not_empty_me = 0   #num of none empty lines
            weight_nonempty_lines = 1.5
            grid_state = numpy.zeros((5,5)) #for storing current move resultant tiles in the wall grid
            move_row = move[2].pattern_line_dest
            move_col = int(my_gs.players[my_id].grid_scheme[move[2].pattern_line_dest][move[2].tile_type])
            for i in range(5): #for each line, not indcluding floor line
                if my_gs.players[my_id].lines_number[i] == i+1: #if line is filled up perfectly
                    tc = my_gs.players[my_id].lines_tile[i] #check tile colour
                    col = int(my_gs.players[my_id].grid_scheme[i][tc]) #check column num of move

                    grid_state[i][col] = 1 #update the current move to grid, here stored in temp matrix grid_state

                    # count the number of tiles in a continguous line
                    # above, below, to the left and right of the placed tile.
                    above = 0
                    for j in range(col-1, -1, -1):
                        val = grid_state[i][j] + my_gs.players[my_id].grid_state[i][j] #current(temp) + old
                        above += val
                        if val == 0:
                            break
                    below = 0
                    for j in range(col+1,5,1):
                        val = grid_state[i][j] + my_gs.players[my_id].grid_state[i][j]
                        below +=  val
                        if val == 0:
                            break
                    left = 0
                    for j in range(i-1, -1, -1):
                        val = grid_state[j][col] + my_gs.players[my_id].grid_state[j][col]
                        left += val
                        if val == 0:
                            break
                    right = 0
                    for j in range(i+1, 5, 1):
                        val = grid_state[j][col] + my_gs.players[my_id].grid_state[j][col]
                        right += val
                        if val == 0:
                            break
                    
                    # If the tile sits in a contiguous vertical line of 
                    # tiles in the grid, it is worth 1*the number of tiles
                    # in this line (including itself).
                    if above > 0 or below > 0:
                        score_inc += (1 + above + below)

                    # In addition to the vertical score, the tile is worth
                    # an additional H points where H is the length of the 
                    # horizontal contiguous line in which it sits.
                    if left > 0 or right > 0:
                        score_inc += (1 + left + right)

                    # If the tile is not next to any already placed tiles
                    # on the grid, it is worth 1 point. 
                    if above == 0 and below == 0 and left == 0 \
                        and right == 0:
                        score_inc += 1
                elif my_gs.players[my_id].lines_number[i] != 0:
                    lines_not_empty_me += 1 #penality given line not empty, our own socring metrics

            # Score penalties for tiles in floor line
            penalties = 0
            floor_num = 0
            for i in range(7):
                floor_num = my_gs.players[my_id].floor[i] + floor_num
            floor_num = move[2].num_to_floor_line + floor_num
            if floor_num >= 7 :
                floor_num = 7
            # logging.debug("floor_num = %s",floor_num)
            for i in range(floor_num):
                penalties += my_gs.players[my_id].FLOOR_SCORES[i]

            #custome scoring metics
            custom_score = weight_nonempty_lines*lines_not_empty_me

            # Players cannot be assigned a negative score in any round.
            score_change = score_inc + penalties
            if score_change < 0 and my_gs.players[my_id].score < -score_change:
                score_change = -my_gs.players[my_id].score

            #end of game bonus score
            rows = my_gs.players[my_id].GetCompletedRows() #past compelted row, cols, set
            cols = my_gs.players[my_id].GetCompletedColumns()
            sets = my_gs.players[my_id].GetCompletedSets()

            #calcualte num of row, cols and set compelted in current move
            row = 0
            column = 0
            current_completed_set = 0
            for i in range(5):
                row = (my_gs.players[my_id].grid_state[move_row][i]) + row
                column = (my_gs.players[my_id].grid_state[i][move_col]) + column
            if row == 4: #if 4 tiles are already filled in , fill in self, = 5,= completed
                rows = rows + 1
            if column == 4:
                cols = cols + 1
            for colour in range(5):
                if my_gs.players[my_id].number_of[colour] == 4 and move[2].tile_type == colour:
                    current_completed_set += 1

            bonus = (rows * 2) + (cols * 7) + ((sets + current_completed_set)* 10)
       
            # return score_change + bonus - custom_score #doesn't work well
            return score_change + bonus

        def tie_bfs(move_1, game_state):
            myQueue = self.Queue() 
            visited = []
            depth = 2
            tie_count = 0
            best_score_me = -999
            best_score_op = -999
            startState = (move_1, depth, self.id, game_state)
            #move, depth, store_move, score_inc, id, gamestate
            myQueue.push(startState)
            visited.append(move_1)
            while not myQueue.isEmpty():
                cur_t = time.perf_counter()-start_time
                state = myQueue.pop()
                move_node, depth, current_id, gs_copy = state
                if current_id == 1: next_id = 0 #switch id for me and opponent
                else: next_id = 1
                gs_copy_2 = copy.deepcopy(gs_copy) #copy, exercute and score before going into next depth
                gs_copy_2.ExecuteMove(current_id, move_node)
                # if current_id == self.id :
                turn_score,_ = gs_copy_2.players[current_id].ScoreRound()
                final_score = gs_copy_2.players[current_id].EndOfGameScore()
                score_inc = final_score + turn_score #only score increase, only updated after pop from queue
                
                #find best score in succ nodes, 3rd depth (depth 0)
                if current_id == self.id and depth == 2: #not the root move_node
                    if score_inc > best_score_me:
                        best_score_me = score_inc

                if current_id == self.opid and depth == 1: #not the root move_node
                    if score_inc > best_score_op:
                        best_score_op = score_inc

                #check goal
                if depth == 0 or cur_t>max_turn_time or not (gs_copy_2.TilesRemaining()):
                    return [best_score_me,best_score_op]

                #push new node
                next_move_node = gs_copy_2.players[next_id].GetAvailableMoves(gs_copy_2)
                for next_move in next_move_node:
                    if next_move not in visited:
                        newstate = (next_move, (depth - 1), next_id, gs_copy_2) #store_move remains the same
                        myQueue.push(newstate)
                        visited.append(next_move)

        #rank moves, then find ties in ranking and write to new_move
        moves.sort(key = lambda move: ScoreRound(move, self.id,game_state), reverse = True)
        for i in moves:
            if ScoreRound(i, self.id,game_state) == ScoreRound(moves[0], self.id,game_state):
                new_move.append(i)

        for move_1 in new_move:
            gs_copy = copy.deepcopy(game_state)
            best_score_me, best_score_op = tie_bfs(move_1, gs_copy)
            if best_score_me > best_score_kid:
                best_score_kid = best_score_me #update best score for successor node in depth 3
                best_move = move_1       #update best_move based on successor score
            elif best_score_me == best_score_kid: #tie break using op score
                if best_score_op < worst_score_kid_op:
                    worst_score_kid_op = best_score_op
                    best_move = move_1 
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