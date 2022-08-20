import numpy as np
from clue import Clue
from node import Node
from utils import manhattan_distance


class Board:
    """
    Contains the board of the game.
    Useful parameters:
    - board_w: width of the board
    - board_h: height of the board
    - state: current state of the board
    """

    Counter = 0

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
            if length > 1:
                clue = Clue(x=x, y=y, length=length, color=color)
                self.clues.append(clue)
                self.set(x, y, clue)
            else:
                # If length is 1, then we can automatically color it
                self.set(x, y, Node(x=x, y=y, color=color, length=length))
        self.board_w = len(self.state)
        self.board_h = len(self.state[0])

    def calculate_all_paths(self):
        for clue in self.clues:
            clue.calculate_paths(board=self)
        self.clues.sort()

    def get(self, x, y):
        return self.state[x, y]

    def set(self, x, y, value):
        self.state[x, y] = value

    def is_valid_position(self, x, y):
        return 0 <= x < self.board_w and 0 <= y < self.board_h

    def pretty_print(self):
        for x in range(len(self.state)):
            for y in range(len(self.state[0])):
                v = self.get(x, y)
                print('00' if v == 0 else v, end=' ')
            print()

    def remove_clue(self, x, y):
        clue = self.get(x, y)
        self.clues.remove(clue)

    def fill_path(self, path, color, length):
        # Remove target clue from board
        target_x, target_y = path[-1]
        self.remove_clue(target_x, target_y)

        # Add colored nodes to board
        for i, (x, y) in enumerate(path):
            if i == 0 or i == len(path) - 1:
                self.set(x, y, Node(x=x, y=y, color=color, length=length))
            else:
                self.set(x, y, Node(x=x, y=y, color=color))

    def sort_by_proximity(self, path):
        ret = 0
        for position in path:
            x, y = position
            if x - 1 < 0 or self.get(x - 1, y) != 0:
                ret -= 1
            if x + 1 >= self.board_w or self.get(x + 1, y) != 0:
                ret -= 1
            if y - 1 < 0 or self.get(x, y - 1) != 0:
                ret -= 1
            if y + 1 >= self.board_h or self.get(x, y + 1) != 0:
                ret -= 1
        return ret

    def reevaluate_clues(self, path):
        for clue in self.clues:
            if any(manhattan_distance((clue.x, clue.y), (x, y)) <= clue.length for x, y in path):
                # Check if all paths of the clue are now blocked
                clue.paths[:] = [old_path for old_path in clue.paths if not any(x in old_path[1:] for x in path)]
                if len(clue.paths) == 0:
                    return False
                #clue.paths.sort(key=self.sort_by_proximity)
        self.clues.sort()
        return True

    def __deepcopy__(self):
        Board.Counter += 1
        new_board = Board()
        new_board.board_h = self.board_h
        new_board.board_w = self.board_w
        new_board.state = self.state.copy()
        new_board.clues = []
        for clue in self.clues:
            clue_copy = clue.__deepcopy__()
            new_board.clues.append(clue_copy)
            new_board.set(clue.x, clue.y, clue_copy)
        return new_board



