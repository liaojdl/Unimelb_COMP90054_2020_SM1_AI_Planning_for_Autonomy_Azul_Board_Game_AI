# Written by Michelle Blom, 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from utils import *
from enum import IntEnum
import model
import numpy
import random
import abc
from advance_model import *
import copy
import sys
import time
import inspect
import heapq
import logging
logging.basicConfig(level=logging.DEBUG)

class myPlayer(AdvancePlayer):
    def __init__(self, _id):
        super().__init__(_id)
        # sort out who is who
        if self.id == 1:
            self.opid = 0
        else:
            self.opid = 1

    def SelectMove(self, moves, game_state):

        gsx = Round_State2(2)
        gsx.players = game_state.players
        gsx.factories = game_state.factories
        gsx.centre_pool = game_state.centre_pool
        gsx.bag = game_state.bag
        gsx.bag_used = game_state.bag_used
        gsx.first_player_taken = game_state.first_player_taken
        gsx.first_player = game_state.first_player
        gsx.next_first_player = game_state.next_first_player
        logging.debug(BoardToString(game_state))
        logging.debug(BoardToString(gsx))

        ## Select moves that maximises per turn score return
        best_turn_score = -999
        best_move = None
        for move in moves:
            # copy for prediction
            gs_copy = copy.deepcopy(gsx)
            gs_copy.ExecuteMove1(self.id,move)
            turn_score,_ = gs_copy.players[self.id].ScoreRound()
            if turn_score > best_turn_score:
                best_move = move
                best_turn_score = turn_score
        return best_move


class Round_State2:
    NUM_FACTORIES = [5,7,9]
    NUM_TILE_TYPE = 20
    NUM_ON_FACTORY = 4

    def __init__(self, num_players):
        # Create player states
        self.players = []
        for i in range(num_players):
            ps = PlayerState(i)
            self.players.append(ps)
            
        # Tile bag contains NUM_TILE_TYPE of each tile colour
        self.bag = []
        for i in range(self.NUM_TILE_TYPE):
            self.bag.append(Tile.BLUE)
            self.bag.append(Tile.YELLOW)
            self.bag.append(Tile.RED)
            self.bag.append(Tile.BLACK)
            self.bag.append(Tile.WHITE)

        # Shuffle contents of tile bag
        random.shuffle(self.bag)

        # "Used" bag is initial empty
        self.bag_used = []

        # In a 2/3/4-player game, 5/7/9 factory displays are used
        self.factories = []
        for i in range(self.NUM_FACTORIES[num_players-2]):
            td = TileDisplay()
            
            # Initialise factory display: add NUM_ON_FACTORY randomly
            # drawn tiles to the factory (if available). 
            self.InitialiseFactory(td)
            self.factories.append(td)

        self.centre_pool = TileDisplay()
        self.first_player_taken = False
        self.first_player = random.randrange(num_players)
        self.next_first_player = -1


    def TilesRemaining(self):
        if self.centre_pool.total > 0:
            return True
        for fac in self.factories:
            if fac.total > 0:
                return True
        return False

    # Place tiles from the main bag (and used bag if the main bag runs
    # out of tiles) onto the given factory display.
    def InitialiseFactory(self, factory):
        # Reset contents of factory display
        factory.total = 0
        for tile in Tile:
            factory.tiles[tile] = 0

        # If there are < NUM_ON_FACTORY tiles in the bag, shuffle the 
        # tiles in the "used" bag and add them to the main bag (we still
        # want the tiles that were left in the main bag to be drawn first).
        # Fill the factory display with tiles, up to capacity, if possible.
        # If there are less than NUM_ON_FACTORY tiles available in both
        # bags, the factory will be left at partial capacity.
        if len(self.bag) < self.NUM_ON_FACTORY and len(self.bag_used) > 0:
            random.shuffle(self.bag_used)
            self.bag.extend(self.bag_used)
            self.bag_used = []

        for i in range(min(self.NUM_ON_FACTORY,len(self.bag))):
            # take tile out of the bag
            tile = self.bag.pop(0)
            factory.tiles[tile] += 1
            factory.total += 1


    # Setup a new round of play be resetting each of the factory displays
    # and the centre tile pool
    def SetupNewRound(self):
        # Reset contents of each factory display
        for fd in self.factories:
            self.InitialiseFactory(fd)

        for tile in Tile:
            self.centre_pool.tiles[tile] = 0

        self.first_player_taken = False
        self.first_player = self.next_first_player
        self.next_first_player = -1

        for plr in self.players:
            plr.player_trace.StartRound()


    # Execute end of round actions (scoring and clean up)
    def ExecuteEndOfRound(self):
        # Each player scores for the round, and we add tiles to the 
        # used bag (if appropriate).
        for plr in self.players:
            _,used = plr.ScoreRound()
            self.bag_used.extend(used)


    # Execute move by given player
    def ExecuteMove1(self, player_id, move):
        plr_state = self.players[player_id]
        plr_state.player_trace.moves[-1].append(move)

        # The player is taking tiles from the centre
        if move[0] == Move.TAKE_FROM_CENTRE: 
            tg = move[2]

            if not self.first_player_taken:
                plr_state.GiveFirstPlayerToken()
                self.first_player_taken = True
                self.next_first_player = player_id

            if tg.num_to_floor_line > 0:
                ttf = []
                for i in range(tg.num_to_floor_line):
                    ttf.append(tg.tile_type)
                plr_state.AddToFloor(ttf)
                self.bag_used.extend(ttf)

            if tg.num_to_pattern_line > 0:
                plr_state.AddToPatternLine(tg.pattern_line_dest, 
                    tg.num_to_pattern_line, tg.tile_type)

            # Remove tiles from the centre
            self.centre_pool.RemoveTiles(tg.number, tg.tile_type)

        elif move[0] == Move.TAKE_FROM_FACTORY:
            tg = move[2]
            if tg.num_to_floor_line > 0:
                ttf = []
                for i in range(tg.num_to_floor_line):
                    ttf.append(tg.tile_type)
                plr_state.AddToFloor(ttf)
                self.bag_used.extend(ttf)

            if tg.num_to_pattern_line > 0:
                plr_state.AddToPatternLine(tg.pattern_line_dest, 
                    tg.num_to_pattern_line, tg.tile_type)

            # Remove tiles from the factory display
            fid = move[1]
            fac = self.factories[fid]
            fac.RemoveTiles(tg.number,tg.tile_type)

            # All remaining tiles on the factory display go into the 
            # centre!
            for tile in Tile:
                num_on_fd = fac.tiles[tile]
                if num_on_fd > 0:
                    self.centre_pool.AddTiles(num_on_fd, tile)
                    fac.RemoveTiles(num_on_fd, tile)

# The GameState class encapsulates the state of the game: the game 
# state for each player; the state of the factory displays and 
# centre tile pool; and the state of the tile bags. 
class Round_State:
    NUM_FACTORIES = 5
    NUM_TILE_TYPE = 20
    NUM_ON_FACTORY = 4

    def __init__(self):
        # Create player states
        self.players = []
        for i in range(2):
            ps = PlayerState(i)
            self.players.append(ps)

        # In a 2/3/4-player game, 5/7/9 factory displays are used
        self.factories = []
        for i in range(self.NUM_FACTORIES):
            td = TileDisplay()
            self.factories.append(td)

        self.centre_pool = TileDisplay()


    def TilesRemaining(self):
        if self.centre_pool.total > 0:
            return True
        for fac in self.factories:
            if fac.total > 0:
                return True
        return False


    # Execute move by given player
    def ExecuteMove(self, player_id, move):
        plr_state = self.players[player_id]

        # The player is taking tiles from the centre
        if move[0] == Move.TAKE_FROM_CENTRE: 
            tg = move[2]
            if tg.num_to_floor_line > 0:
                ttf = []
                for i in range(tg.num_to_floor_line):
                    ttf.append(tg.tile_type)
                plr_state.AddToFloor(ttf)

            if tg.num_to_pattern_line > 0:
                plr_state.AddToPatternLine(tg.pattern_line_dest, 
                    tg.num_to_pattern_line, tg.tile_type)

            # Remove tiles from the centre
            self.centre_pool.RemoveTiles(tg.number, tg.tile_type)

        elif move[0] == Move.TAKE_FROM_FACTORY:
            tg = move[2]
            if tg.num_to_floor_line > 0:
                ttf = []
                for i in range(tg.num_to_floor_line):
                    ttf.append(tg.tile_type)
                plr_state.AddToFloor(ttf)

            if tg.num_to_pattern_line > 0:
                plr_state.AddToPatternLine(tg.pattern_line_dest, 
                    tg.num_to_pattern_line, tg.tile_type)

            # Remove tiles from the factory display
            fid = move[1]
            fac = self.factories[fid]
            fac.RemoveTiles(tg.number,tg.tile_type)

            # All remaining tiles on the factory display go into the 
            # centre!
            for tile in Tile:
                num_on_fd = fac.tiles[tile]
                if num_on_fd > 0:
                    self.centre_pool.AddTiles(num_on_fd, tile)
                    fac.RemoveTiles(num_on_fd, tile)

# There are 5 types of tiles in the game, each differentiated by colour.
class Tile(IntEnum):
    BLUE = 0
    YELLOW = 1
    RED = 2
    BLACK = 3
    WHITE = 4

# There are 2 types of moves a player can perform in the game
class Move(IntEnum):
    TAKE_FROM_FACTORY = 1
    TAKE_FROM_CENTRE = 2

# Structure recording the number, type, and destination of tiles 
# collected by a player. Note that the sum of 'num_to_pattern_line'
# and 'num_to_floor_line' must equal 'number'.
class TileGrab:
    def __init__(self):
        self.tile_type = -1
        self.number = 0
        self.pattern_line_dest = -1
        self.num_to_pattern_line = 0
        self.num_to_floor_line = 0 

# We use the tile display class to represent both factory displays and 
# the pool of tiles in the centre of the playing area. 
class TileDisplay:
    def __init__(self):
        # Map between tile colour and number in the display
        self.tiles = {}

        # Total number of tiles in the display
        self.total = 0

        for tile in Tile:
            self.tiles[tile] = 0

    def RemoveTiles(self, number, tile_type):
        assert number > 0
        assert tile_type in Tile
        assert tile_type in self.tiles

        self.tiles[tile_type] -= number
        self.total -= number

        assert self.tiles[tile_type] >= 0
        assert self.total >= 0

    def AddTiles(self, number, tile_type):
        assert number > 0
        assert tile_type in Tile
        assert tile_type in self.tiles
        
        self.tiles[tile_type] += number
        self.total += number

# Bundle together a player's activity in the game for use in
# updating a policy
class PlayerTrace:
    def __init__(self, pid):
        # Player ID
        self.id = pid

        # Round by round move history
        self.moves = []
    
        # Round by round scores
        self.round_scores = []

        # Bonus scores
        self.bonuses = 0

    def StartRound(self):
        self.moves.append(list())
        self.round_scores.append(0)
