import numpy as np
from clue import Clue

class Board:
    """
    Contains the board of the game.
    Useful parameters:
    - board_w: width of the board
    - board_h: height of the board
    - state: current state of the board
    """

    def __init__(self, mat_data):
        self.board_h, self.board_w, self.state = None, None, None
        self.clues = {}
        self.parse_mat(mat_data)

    def load_board(self, state, board_w, board_h):
        self.board_w = board_w
        self.board_h = board_h
        self.state = state

    def parse_mat(self, mat_data):
        mat = np.zeros((mat_data['total_col'][0, 0], mat_data['total_row'][0, 0]), dtype=tuple)
        for mat_link in mat_data['puzzledata']:
            x, y = mat_link[2] - 1, mat_link[3] - 1
            length, color = mat_link[0], mat_link[1]
            if length > 2:
                self.clues[(x, y)] = Clue(x=x, y=y, length=length, color=color)
                mat[x, y] = self.clues[(x, y)]
        state = mat
        width = len(state)
        height = len(state[0])
        self.load_board(state=state, board_w=width, board_h=height)

    def calculate_all_paths(self):
        for clue in self.clues.values():
            clue.calculate_all_paths(board=self)

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
