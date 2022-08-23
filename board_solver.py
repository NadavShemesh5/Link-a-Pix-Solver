import numpy as np
from scipy.optimize import linprog
from contstants import USE_LINEAR_STEP
from node import Node
from timetester import TimeTester


class BoardSolver:
    def __init__(self, board):
        self.board = board

    def is_complete(self):
        if not self.board.clues:
            self.board.pretty_print()
            return True

    def get_next_clue(self):
        current_clue = min(self.board.clues)
        self.board.remove_clue(self.board.clues, current_clue)
        clue_paths = current_clue.paths
        TimeTester.time("sort_by_proximity")
        current_clue.paths.sort(key=self.board.sort_by_proximity)
        TimeTester.time("sort_by_proximity")
        return current_clue, clue_paths

    def handle_clue_path(self, clue, path):
        # Fill the path's of the clue with the clue's color
        self.board.fill_path(path=path, color=clue.color, length=clue.length)
        # Check if other paths were blocked
        if not self.board.reevaluate_clues(clues_list=self.board.clues, path=path):
            # A clue has no possible paths! Aborting...
            return False
        if self.is_complete():
            return True
        return None

    def solve(self):
        # Calculate the possible paths for all clues
        TimeTester.time("calculate_all_paths")
        self.board.calculate_all_paths()
        TimeTester.time("calculate_all_paths")

        handle_res = self.deterministic_step()
        if handle_res is True:
            return True

        if USE_LINEAR_STEP:
            handle_res = self.linear_programming_step()
            if handle_res is True:
                return True

        return self.recursive_step()

    def deterministic_step(self):
        if self.is_complete():
            return True

        # Get first clue to solve
        current_clue, clue_paths = self.get_next_clue()

        while len(clue_paths) == 1:
            # Handle the path
            handle_res = self.handle_clue_path(clue=current_clue, path=clue_paths[0])
            if handle_res is True:
                return handle_res
            # Get the next clue
            current_clue, clue_paths = self.get_next_clue()

        self.board.clues.insert(0, current_clue)
        return False

    def recursive_step(self):
        # Get the next clue to solve
        current_clue, clue_paths = self.get_next_clue()

        if len(clue_paths) == 0:
            # No paths found! Aborting...
            return False
        else:
            while len(clue_paths) == 1:
                # Handle the path
                handle_res = self.handle_clue_path(clue=current_clue, path=clue_paths[0])
                if handle_res is True or handle_res is False:
                    return handle_res
                # Get the next clue
                current_clue, clue_paths = self.get_next_clue()
            for path in clue_paths:
                board_solver = BoardSolver(self.board.__deepcopy__())
                handle_res = board_solver.handle_clue_path(clue=current_clue, path=path)
                if handle_res is False:
                    continue
                elif handle_res or board_solver.recursive_step():
                    return True

    def init_map_zero(self):
        map_zero = np.ones(self.board.board_w * self.board.board_h)
        offset = 0
        for y in range(self.board.board_h):
            for x in range(self.board.board_w):
                if isinstance(self.board.state[x, y], Node) and not self.board.state[x, y].is_clue:
                    map_zero[offset + x] = 0
            offset += self.board.board_w
        return map_zero

    def init_paths_list(self):
        paths = set()
        for clue in self.board.clues:
            for path in clue.paths:
                if not path[::-1] in paths:
                    paths.add(path)
        return list(paths)

    def init_map_from_path(self, path):
        curr_map = np.zeros(self.board.board_w * self.board.board_h)
        for position in path:
            x, y = position
            curr_map[y * self.board.board_w + x] = 1
        return curr_map

    def linear_programming_step(self):
        maps = [self.init_map_zero()]
        paths = self.init_paths_list()
        for path in paths:
            maps.append(self.init_map_from_path(path))

        # Init variables
        maps = np.stack(maps, axis=1)
        b_ub = np.zeros(self.board.board_w * self.board.board_h)
        c = np.full(maps.shape[1], -1.)
        lb = np.ones(maps.shape[1])
        lb[0] = -1
        ub = np.zeros(maps.shape[1])
        ub[0] = -1
        bounds = np.column_stack((ub, lb))
        sol = linprog(c=c, A_ub=maps, b_ub=b_ub, bounds=bounds)

        # Solved case
        if not np.any(np.mod(sol['x'], 1) != 0):
            for i in range(1, len(sol['x'])):
                if sol['x'][i] == 1:
                    path = paths[i - 1]
                    x, y = path[0]
                    current_clue = self.board.state[x, y]
                    self.board.fill_path(path=path, color=current_clue.color, length=current_clue.length, remove_target_clue=True)
            self.board.pretty_print()
            return True

        # Unsolved case
        for i in range(1, len(sol['x'])):
            if sol['x'][i] > 0.501:
                path = paths[i - 1]
                x, y = path[0]
                current_clue = self.board.state[x, y]
                self.board.clues.remove(current_clue)
                handle_res = self.handle_clue_path(clue=current_clue, path=path)
                if handle_res:
                    return True

        return False
