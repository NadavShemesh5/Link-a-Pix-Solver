import numpy as np
from clue import Clue
from contstants import PRINT_BOARD
from node import Node
from timetester import TimeTester
import copy

class Board:
    """
    Contains the board of the game.
    Useful parameters:
    - board_w: width of the board
    - board_h: height of the board
    - state: current state of the board
    """

    def __init__(self, mat_data=None):
        self.board_h, self.board_w, self.state = None, None, None
        self.clues = []
        if mat_data is not None:
            self.parse_mat(mat_data)

    def parse_mat(self, mat_data):
        self.state = np.zeros((mat_data['total_col'][0, 0], mat_data['total_row'][0, 0]), dtype=tuple)
        for mat_link in mat_data['puzzledata']:
            x, y = mat_link[2] - 1, mat_link[3] - 1
            length, color = mat_link[0], mat_link[1]
            if length > 2:
                clue = Clue(x=x, y=y, length=length, color=color)
                self.clues.append(clue)
                self.state[x, y] = clue
            else:
                # If length is 1, then we can automatically color it
                self.state[x, y] = Node(x=x, y=y, color=color, length=length)
        self.board_w = len(self.state)
        self.board_h = len(self.state[0])

    def calculate_all_paths(self):
        for clue in self.clues:
            clue.calculate_paths(board=self)
        self.clues.sort()

    def is_valid_position(self, x, y):
        return 0 <= x < self.board_w and 0 <= y < self.board_h

    def pretty_print(self):
        if not PRINT_BOARD:
            return
        print("-------------------------------")
        for x in range(len(self.state)):
            for y in range(len(self.state[0])):
                v = self.state[x, y]
                print('00' if v == 0 else v, end=' ')
            print()

    def fill_path(self, path, color, length):
        # Remove target clue from board
        self.clues.remove(self.state[path[-1]])
        # Add colored nodes to board
        for i, (x, y) in enumerate(path):
            if i == 0 or i == len(path) - 1:
                self.state[x, y] = Node(x=x, y=y, color=color, length=length)
            else:
                self.state[x, y] = Node(x=x, y=y, color=color)

    def sort_by_proximity(self, path):
        ret = 0
        for x, y in path:
            if x - 1 < 0:
                ret -= 1
            elif self.state[x - 1, y] != 0:
                ret -= 1
            if x + 1 >= self.board_w:
                ret -= 1
            elif self.state[x + 1, y] != 0:
                ret -= 1
            if y - 1 < 0:
                ret -= 1
            elif self.state[x, y - 1] != 0:
                ret -= 1
            if y + 1 >= self.board_h:
                ret -= 1
            elif self.state[x, y + 1] != 0:
                ret -= 1
        return ret

    def reevaluate_clues(self, path):
        TimeTester.time("reevaluate_clues")
        for clue in self.clues:
            for xy in path:
                if xy in clue.general_paths_dicts:

                    TimeTester.time("check_blocked")
                    for i in reversed(range(len(clue.paths_dicts))):
                        if xy in clue.paths_dicts[i]:
                            clue.paths.remove(clue.paths_dicts[i][xy])
                            del clue.paths_dicts[i]
                    del clue.general_paths_dicts[xy]
                    TimeTester.time("check_blocked")

                    if len(clue.paths) == 0:
                        TimeTester.time("reevaluate_clues")
                        return False
        TimeTester.time("reevaluate_clues")
        return True

    def __deepcopy__(self, memo={}):
        TimeTester.DeepCopies += 1
        new_board = Board()
        new_board.board_h = self.board_h
        new_board.board_w = self.board_w
        new_board.state = np.copy(self.state)
        new_board.clues = []
        new_board.removed_clues = {}
        for clue in self.clues:
            clue_copy = clue.__deepcopy__()
            new_board.clues.append(clue_copy)
            new_board.state[clue.x, clue.y] = clue_copy
        return new_board
