"""Generic utility functions
"""
# from __future__ import print_function
from threading import Thread
from multiprocessing import Queue
import time
import copy

INFINITY = float(6000)


class ExceededTimeError(RuntimeError):
    """Thrown when the given function exceeded its runtime.
    """
    pass


def function_wrapper(func, args, kwargs, result_queue):
    """Runs the given function and measures its runtime.

    :param func: The function to run.
    :param args: The function arguments as tuple.
    :param kwargs: The function kwargs as dict.
    :param result_queue: The inter-process queue to communicate with the parent.
    :return: A tuple: The function return value, and its runtime.
    """
    start = time.time()
    try:
        result = func(*args, **kwargs)
    except MemoryError as e:
        result_queue.put(e)
        return

    runtime = time.time() - start
    result_queue.put((result, runtime))


def run_with_limited_time(func, args, kwargs, time_limit):
    """Runs a function with time limit

    :param func: The function to run.
    :param args: The functions args, given as tuple.
    :param kwargs: The functions keywords, given as dict.
    :param time_limit: The time limit in seconds (can be float).
    :return: A tuple: The function's return value unchanged, and the running time for the function.
    :raises PlayerExceededTimeError: If player exceeded its given time.
    """
    q = Queue()
    t = Thread(target=function_wrapper, args=(func, args, kwargs, q))
    t.start()

    # This is just for limiting the runtime of the other thread, so we stop eventually.
    # It doesn't really measure the runtime.
    t.join(time_limit)

    if t.is_alive():
        raise ExceededTimeError

    q_get = q.get()
    if isinstance(q_get, MemoryError):
        raise q_get
    return q_get


class MiniMaxAlgorithm:

    def __init__(self, utility, my_color, no_more_time, selective_deepening):
        """Initialize a MiniMax algorithms without alpha-beta pruning.

        :param utility: The utility function. Should have state as parameter.
        :param my_color: The color of the player who runs this MiniMax search.
        :param no_more_time: A function that returns true if there is no more time to run this search, or false if
                             there is still time left.
        :param selective_deepening: A functions that gets the current state, and
                        returns True when the algorithm should continue the search
                        for the minimax value recursivly from this state.
                        optional
        """
        self.utility = utility
        self.my_color = my_color
        self.no_more_time = no_more_time
        self.selective_deepening = selective_deepening

    def search(self, state, depth, maximizing_player):
        """Start the MiniMax algorithm.

        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The move in case of max node or None in min mode)
        """

        children = state.get_possible_moves()

        if (0 == len(children)) or (0 == depth) or (self.no_more_time()):
            return self.utility(state), None

        turn = state.curr_player
        best_move = None

        if turn == self.my_color:
            curr_max = -INFINITY
            for c in children:
                c_state = copy.deepcopy(state)
                c_state.perform_move(c[0], c[1])
                c_val, _ = self.search(c_state, depth - 1, not maximizing_player)
                if c_val > curr_max:
                    curr_max = c_val
                    best_move = c
            return curr_max, best_move
        else:
            curr_min = INFINITY
            for c in children:
                c_state = copy.deepcopy(state)
                c_state.perform_move(c[0], c[1])
                c_val, _ = self.search(c_state, depth - 1, not maximizing_player)
                if c_val < curr_min:
                    curr_min = c_val
            return curr_min, None


class MiniMaxWithAlphaBetaPruning:

    def __init__(self, utility, my_color, no_more_time, selective_deepening):
        """Initialize a MiniMax algorithms with alpha-beta pruning.

        :param utility: The utility function. Should have state as parameter.
        :param my_color: The color of the player who runs this MiniMax search.
        :param no_more_time: A function that returns true if there is no more time to run this search, or false if
                             there is still time left.
        :param selective_deepening: A functions that gets the current state, and
                        returns True when the algorithm should continue the search
                        for the minimax value recursivly from this state.
        """
        self.utility = utility
        self.my_color = my_color
        self.no_more_time = no_more_time
        self.selective_deepening = selective_deepening

    def search(self, state, depth, alpha, beta, maximizing_player):
        """Start the MiniMax algorithm.

        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param alpha: The alpha of the alpha-beta pruning.
        :param beta: The beta of the alpha-beta pruning.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The alpha-beta algorithm value, The move in case of max node or None in min mode)
        """
        return self.utility(state), None
