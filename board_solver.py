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
        self.solve2()

    def solve2(self):
        if self.is_complete():
            return True

        # Get the next clue to solve
        current_clue, clue_paths = self.get_next_clue()

        if len(clue_paths) == 0:
            print("No paths found! Aborting...")
            return False
        else:
            while len(clue_paths) == 1:
                # Fill that sole path
                path = clue_paths[0]
                self.board.fill_path(path=path, color=current_clue.color)
                # Reevaluate the clues and sort them
                if not self.board.reevaluate_clues(path=path):
                    print("A clue has no possible paths! Aborting...")
                    return False
                if self.is_complete():
                    return True
                # Get the next clue
                current_clue, clue_paths = self.get_next_clue()

            for path in clue_paths:
                new_board = self.board.__deepcopy__()
                new_board.fill_path(path=path, color=current_clue.color)
                if not new_board.reevaluate_clues(path=path):
                    continue
                if BoardSolver(new_board).solve2():
                    return True

