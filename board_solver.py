import time

from board import Board
import copy


class BoardSolver:
    def __init__(self, board):
        self.board = board

    def is_complete(self):
        if not self.board.clues:
            self.board.pretty_print()
            return True

    def get_next_clue(self):
        current_clue = self.board.clues.pop(0)
        clue_paths = current_clue.paths
        return current_clue, clue_paths

    def solve(self):
        # Calculate the possible paths for all clues
        self.board.calculate_all_paths()
        return self.solve_helper()

    def handle_clue_path(self, clue, path):
        # Fill the path's of the clue with the clue's color
        self.board.fill_path(path=path, color=clue.color, length=clue.length)
        # Reevaluate the clues and sort them
        if not self.board.reevaluate_clues(path=path):
            # A clue has no possible paths! Aborting...
            return False
        if self.is_complete():
            return True
        return None

    def solve_helper(self):
        if self.is_complete():
            return True

        # Get the next clue to solve
        current_clue, clue_paths = self.get_next_clue()

        if len(clue_paths) == 0:
            # No paths found! Aborting...
            return False
        else:
            while len(clue_paths) == 1:
                # Fill that sole path
                path = clue_paths[0]
                handle_res = self.handle_clue_path(clue=current_clue, path=path)
                if handle_res is True:
                    return True
                if handle_res is False:
                    return False
                # Get the next clue
                current_clue, clue_paths = self.get_next_clue()

            for path in clue_paths:
                new_board = self.board.__deepcopy__()
                board_solver = BoardSolver(new_board)
                handle_res = board_solver.handle_clue_path(clue=current_clue, path=path)
                if handle_res is False:
                    continue
                if board_solver.solve_helper():
                    return True
