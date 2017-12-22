# ===============================================================================
# Imports
# ===============================================================================

import abstract
from Reversi.board import GameState
from opening_book import OpeningBook
from utils import INFINITY, run_with_limited_time, ExceededTimeError
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
import time
import copy
from collections import defaultdict


# ===============================================================================
# Player
# ===============================================================================

class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        self.book = OpeningBook()
        self.prev_state = GameState()
        self.moves_list = ""
        self.book_to_our_dic = self.build_book_to_our_dic()
        self.our_to_book_dic = self.build_our_to_book_dic()

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            return possible_moves[0]

        best_move = self.opening_move(game_state)

        if best_move == None:
            best_move = possible_moves[0]
            next_state = copy.deepcopy(game_state)
            next_state.perform_move(best_move[0], best_move[1])
            # Choosing an arbitrary move
            # Get the best move according the utility function
            for move in possible_moves:
                new_state = copy.deepcopy(game_state)
                new_state.perform_move(move[0], move[1])
                if self.utility(new_state) > self.utility(next_state):
                    next_state = new_state
                    best_move = move
            self.moves_list = self.moves_list+"+"+self.our_to_book_dic[best_move[0]][best_move[1]]
            self.prev_state=next_state

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        return best_move

    def utility(self, state):
        mobility_adv = self.mobility_adv(state)
        if mobility_adv > 100 or mobility_adv < -100:
            return mobility_adv

        coin_adv = self.coin_adv(state)
        if coin_adv > 100 or coin_adv < -100:
            return coin_adv

        corner_adv = self.corner_adv(state)
        corner_closeness_adv = self.corner_closeness_adv(state)

        # TODO: fix Word file
        weight_total_adv = (0.50 * coin_adv) + (0.30 * corner_adv) + (0.15 * corner_closeness_adv) + (
                0.05 * mobility_adv)

        return weight_total_adv

    def coin_adv(self, state):
        my_coins = 0
        op_coins = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_coins += 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_coins += 1

        if my_coins == 0:
            # I have no tools left
            return -INFINITY
        elif op_coins == 0:
            # The opponent has no tools left
            return INFINITY

        if my_coins > op_coins:
            coin_adv = (100.0 * my_coins) / (my_coins + op_coins)
        elif my_coins < op_coins:
            coin_adv = -(100.0 * op_coins) / (my_coins + op_coins)
        else:
            coin_adv = 0

        return coin_adv

    def corner_adv(self, state):
        me, op = self.get_colors()
        my_corners = 0
        op_corners = 0
        if state.board[0][0] == me:
            my_corners += 1
        elif state.board[0][0] == op:
            op_corners += 1
        if state.board[0][7] == me:
            my_corners += 1
        elif state.board[0][7] == op:
            op_corners += 1
        if state.board[7][0] == me:
            my_corners += 1
        elif state.board[7][0] == op:
            op_corners += 1
        if state.board[7][7] == me:
            my_corners += 1
        elif state.board[7][7] == op:
            op_corners += 1

        corner_adv = 25 * (my_corners - op_corners)

        return corner_adv

    def get_colors(self):
        me = self.color
        if me == 'O':
            op = 'X'
        else:
            op = 'O'
        return me, op

    def corner_closeness_adv(self, state):
        me, op = self.get_colors()
        my_coins = 0
        op_coins = 0

        if state.board[0][0] == EM:
            if state.board[0][1] == me:
                my_coins += 1
            elif state.board[0][1] == op:
                op_coins += 1
            if state.board[1][1] == me:
                my_coins += 1
            elif state.board[1][1] == op:
                op_coins += 1
            if state.board[1][0] == me:
                my_coins += 1
            elif state.board[1][0] == op:
                op_coins += 1

        if state.board[0][7] == EM:
            if state.board[0][6] == me:
                my_coins += 1
            elif state.board[0][6] == op:
                op_coins += 1
            if state.board[1][6] == me:
                my_coins += 1
            elif state.board[1][6] == op:
                op_coins += 1
            if state.board[1][7] == me:
                my_coins += 1
            elif state.board[1][7] == op:
                op_coins += 1

        if state.board[7][0] == EM:
            if state.board[7][1] == me:
                my_coins += 1
            elif state.board[7][1] == op:
                op_coins += 1
            if state.board[6][1] == me:
                my_coins += 1
            elif state.board[6][1] == op:
                op_coins += 1
            if state.board[6][0] == me:
                my_coins += 1
            elif state.board[6][0] == op:
                op_coins += 1

        if state.board[7][7] == EM:
            if state.board[6][7] == me:
                my_coins += 1
            elif state.board[6][7] == op:
                op_coins += 1
            if state.board[6][6] == me:
                my_coins += 1
            elif state.board[6][6] == op:
                op_coins += 1
            if state.board[7][6] == me:
                my_coins += 1
            elif state.board[7][6] == op:
                op_coins += 1

        corner_closeness = -8.333 * (my_coins - op_coins)

        return corner_closeness

    def mobility_adv(self, state):
        me, op = self.get_colors()

        my_state = copy.deepcopy(state)
        my_state.curr_player = me
        my_possible_moves = len(my_state.get_possible_moves())
        if my_possible_moves == 0:
            return -INFINITY

        op_state = copy.deepcopy(state)
        op_state.curr_player = op
        op_possible_moves = len(op_state.get_possible_moves())
        if op_possible_moves == 0:
            return INFINITY

        if my_possible_moves > op_possible_moves:
            mobility = (100.0 * my_possible_moves) / (my_possible_moves + op_possible_moves)
        elif my_possible_moves < op_possible_moves:
            mobility = -(100.0 * op_possible_moves) / (my_possible_moves + op_possible_moves)
        else:
            mobility = 0

        return mobility

    def selective_deepening_criterion(self, state):
        # Better player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better')

    def opening_move(self, state):
        if len(self.moves_list) >= 30:
            return None

        if self.prev_state.board == state.board:
            book_move = self.book.dic[self.moves_list]
            self.moves_list = self.moves_list + book_move
            reg_move = self.book_to_our_dic[book_move[1:3]]
            self.prev_state.perform_move(reg_move[0], reg_move[1])
            return reg_move

        opp_move = self.find_opp_move(state)
        if len(self.moves_list) % 2 == 0:
            opp_move = "+" + opp_move
        else:
            opp_move = "-" + opp_move
        self.moves_list = self.moves_list + opp_move
        self.prev_state = copy.deepcopy(state)
        if self.moves_list in self.book.dic.keys():
            book_move = self.book.dic[self.moves_list]
            self.moves_list = self.moves_list + book_move
            reg_move = self.book_to_our_dic[book_move[1:3]]
            self.prev_state.perform_move(reg_move[0], reg_move[1])
            return reg_move

        return None


    def build_our_to_book_dic(self):
        dic ={}
        for x in range(BOARD_COLS):
            dic[x]={}
            for y in range(BOARD_ROWS):
                key = [x,y]
                val = chr(ord('h')-7+y)+chr(ord('8')-x)
                dic[x][y]=val
        return dic

    def build_book_to_our_dic(self):
        dic ={}
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                key = chr(ord('a')+x)+chr(ord('1')+y)
                val = [7-y,x]
                dic[key]=val
        return dic


    def find_opp_move(self, state):
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if (self.prev_state.board[x][y] == EM and state.board[x][y] != EM and state.board[x][y]):
                    return self.our_to_book_dic[x][y]

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
