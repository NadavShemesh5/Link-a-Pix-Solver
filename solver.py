from scipy.io import loadmat
from scipy.optimize import linprog
import numpy as np
import time


class Link:
    def __init__(self, init_dist, curr_position, color):
        self.init_dist = init_dist
        self.curr_position = curr_position
        self.color = color
        self.possible_paths = []

    def __lt__(self, other):
        if len(self.possible_paths) == len(other.possible_paths):
            return self.init_dist > other.init_dist
        return len(self.possible_paths) < len(other.possible_paths)

    def __gt__(self, other):
        return False

    def __eq__(self, other):
        if not other > -1:
            return self.curr_position == other.curr_position
        return False


class Board:
    def __init__(self, data, width, height):
        self.width = width
        self.height = height
        self.data = data

    def search_helper(self, curr_position, dist_left, init_dist, path, paths, color):
        if dist_left < 1:
            return

        x, y = curr_position
        if not self.data[x, y, 0] > -1:
            if dist_left == 1 and \
                    self.data[x, y, 0].init_dist == init_dist and \
                    self.data[x, y, 0].color == color:
                paths.append(tuple(path + [curr_position]))
            return

        if x != self.width - 1 and (x + 1, y) not in path and not self.data[x + 1, y, 0] > 0:
            self.search_helper((x + 1, y), dist_left - 1, init_dist, path + [curr_position], paths, color)
        if y != self.height - 1 and (x, y + 1) not in path and not self.data[x, y + 1, 0] > 0:
            self.search_helper((x, y + 1), dist_left - 1, init_dist, path + [curr_position], paths, color)
        if x != 0 and (x - 1, y) not in path and not self.data[x - 1, y, 0] > 0:
            self.search_helper((x - 1, y), dist_left - 1, init_dist, path + [curr_position], paths, color)
        if y != 0 and (x, y - 1) not in path and not self.data[x, y - 1, 0] > 0:
            self.search_helper((x, y - 1), dist_left - 1, init_dist, path + [curr_position], paths, color)

    def find_all_paths(self, link):
        ret = []
        x, y = link.curr_position
        if self.data[x, y, 0] > 0:
            return ret
        if x != self.width - 1 and not self.data[x + 1, y, 0] > 0:
            self.search_helper((x + 1, y), link.init_dist - 1, link.init_dist, [(x, y)], ret, link.color)
        if y != self.height - 1 and not self.data[x, y + 1, 0] > 0:
            self.search_helper((x, y + 1), link.init_dist - 1, link.init_dist, [(x, y)], ret, link.color)
        if x != 0 and not self.data[x - 1, y, 0] > 0:
            self.search_helper((x - 1, y), link.init_dist - 1, link.init_dist, [(x, y)], ret, link.color)
        if y != 0 and not self.data[x, y - 1, 0] > 0:
            self.search_helper((x, y - 1), link.init_dist - 1, link.init_dist, [(x, y)], ret, link.color)
        return ret

    def fill_path(self, path, link):
        for (x, y) in path:
            self.data[x, y, :] = (link.init_dist, link.color)

    def pretty_print(self):
        def get_color_coded_str(i):
            return "\033[4{}m{}\033[0m".format(i + 1, " ")

        map_modified = np.vectorize(get_color_coded_str)(self.data[:, :, 1])
        print("\n".join([" ".join(["{}"] * self.width)] * self.height).format(*[x for y in map_modified.tolist() for x in y]))


class LinkSolver:
    def __init__(self, data=None):
        if data is not None:
            self.links = []
            width = len(data)
            height = len(data[0])
            curr_data = np.zeros((width, height, 2), dtype=Link)
            for row in range(width):
                for col in range(height):
                    if data[row, col] != 0:
                        curr_val = data[row, col]
                        curr_data[row, col, :] = (curr_val[0], curr_val[1])
                        if curr_val[0] > 2:
                            curr_link = Link(curr_val[0], (row, col), curr_val[1])
                            curr_data[row, col, :] = curr_link, curr_link.color
                            self.links.append(curr_link)
            self.links.sort(key=lambda x: x.init_dist)
            self.board = Board(curr_data, width, height)
            self.init_paths_for_links()

    def init_paths_for_links(self):
        new_links = []
        for link in self.links:
            paths = self.board.find_all_paths(link)
            if not paths:
                continue
            elif len(paths) == 1:
                path = paths[0]
                x, y = path[-1]
                new_links.append(link)
                new_links.append(self.board.data[x, y, 0])
                self.board.fill_path(path, link)
            else:
                link.possible_paths = paths
        self.links[:] = [x for x in self.links if x not in new_links]
        self.links.sort()

    def reevaluate_links_and_sort(self, path):
        for link in self.links:
            if any(abs(link.curr_position[0] - x[0]) + abs(link.curr_position[1] - x[1])
                   <= link.init_dist for x in path):
                link.possible_paths[:] = [old_path for old_path in link.possible_paths if
                                          not any(x in old_path[1:] for x in path)]
                if len(link.possible_paths) == 0:
                    return False
                # link.possible_paths.sort(key=self.sort_by_proximity)
        self.links.sort()
        return True

    def sort_by_proximity(self, path):
        ret = 0
        for position in path:
            x, y = position
            if x - 1 < 0 or self.board.data[x - 1, y, 0] != 0:
                ret -= 1
            if x + 1 >= self.board.width or self.board.data[x + 1, y, 0] != 0:
                ret -= 1
            if y - 1 < 0 or self.board.data[x, y - 1, 0] != 0:
                ret -= 1
            if y + 1 >= self.board.height or self.board.data[x, y + 1, 0] != 0:
                ret -= 1
        return ret

    def deterministic_step(self):
        if not self.links:
            return True

        curr_link = self.links.pop(0)
        possible_paths = curr_link.possible_paths

        while len(possible_paths) == 1:
            path = possible_paths[0]
            x, y = path[-1]
            self.links.remove(self.board.data[x, y, 0])
            self.board.fill_path(path, curr_link)
            self.reevaluate_links_and_sort(path)
            if not self.links:
                return True
            curr_link = self.links.pop(0)
            possible_paths = curr_link.possible_paths

        self.links.insert(0, curr_link)
        return False

    def linear_programming_step(self):
        maps = []
        map_zero = np.ones(self.board.width * self.board.height)
        for y in range(self.board.height):
            for x in range(self.board.width):
                if self.board.data[x, y, 0] > 0:
                    map_zero[y * self.board.width + x] = 0
        maps.append(map_zero)

        paths = set()
        for link in self.links:
            for path in link.possible_paths:
                if not path[::-1] in paths:
                    paths.add(path)
        paths = list(paths)
        for path in paths:
            curr_map = np.zeros(self.board.width * self.board.height)
            for position in path:
                x, y = position
                curr_map[y * self.board.width + x] = 1
            maps.append(curr_map)

        maps = np.stack(maps, axis=1)
        b_ub = np.zeros(self.board.width * self.board.height)
        c = np.full(maps.shape[1], -1.)
        lb = np.ones(maps.shape[1])
        lb[0] = -1
        ub = np.zeros(maps.shape[1])
        ub[0] = -1
        bounds = np.column_stack((ub, lb))
        sol = linprog(c=c, A_ub=maps, b_ub=b_ub, bounds=bounds)

        if not np.any(np.mod(sol['x'], 1) != 0):
            for i in range(1, len(sol['x'])):
                if sol['x'][i] > 0.501:
                    path = paths[i - 1]
                    x, y = path[0]
                    curr_link = self.board.data[x, y, 0]
                    self.board.fill_path(path, curr_link)
            return True

        for i in range(1, len(sol['x'])):
            if sol['x'][i] > 0.501:
                path = paths[i - 1]
                x, y = path[-1]
                self.links.remove(self.board.data[x, y, 0])
                x, y = path[0]
                curr_link = self.board.data[x, y, 0]
                self.board.fill_path(path, curr_link)
                self.links.remove(curr_link)
                self.reevaluate_links_and_sort(path)

        if not self.links:
            return True
        return False

    def solve(self):
        if self.deterministic_step():
            self.board.pretty_print()
            return

        if self.linear_programming_step():
            self.board.pretty_print()
            return

        self.recursive_step()

    def recursive_step(self):
        if not self.links:
            self.board.pretty_print()
            return True

        curr_link = self.links.pop(0)
        possible_paths = curr_link.possible_paths

        if len(possible_paths) == 0:
            return False

        else:
            while len(possible_paths) == 1:
                path = possible_paths[0]
                x, y = path[-1]
                self.links.remove(self.board.data[x, y, 0])
                self.board.fill_path(path, curr_link)
                if not self.reevaluate_links_and_sort(path):
                    return False
                if not self.links:
                    self.board.pretty_print()
                    return True
                curr_link = self.links.pop(0)
                possible_paths = curr_link.possible_paths

            curr_link.possible_paths.sort(key=self.sort_by_proximity)
            for path in possible_paths:
                new_self = self.fast_copy()
                x, y = path[-1]
                new_self.links.remove(new_self.board.data[x, y, 0])
                new_self.board.fill_path(path, curr_link)
                if not new_self.reevaluate_links_and_sort(path):
                    continue
                if new_self.recursive_step():
                    return True

        return False

    def fast_copy(self):
        new_self = LinkSolver()
        new_data = np.copy(self.board.data)
        new_links = []
        for link in self.links:
            new_link = Link(link.init_dist, link.curr_position, link.color)
            new_link.possible_paths = link.possible_paths[:]
            new_links.append(new_link)
            x, y = new_link.curr_position
            new_data[x, y, 0] = new_link
        new_board = Board(new_data, self.board.width, self.board.height)
        new_self.board = new_board
        new_self.links = new_links
        return new_self

    def __str__(self):
        return self.board.__str__()


if __name__ == '__main__':
    mat_data = loadmat('data_128_128_velocisaurus.mat')
    mat = np.zeros((mat_data['total_col'][0, 0], mat_data['total_row'][0, 0]), dtype=tuple)
    for mat_link in mat_data['puzzledata']:
        mat[mat_link[2] - 1, mat_link[3] - 1] = [mat_link[0], mat_link[1]]

    start_time = time.time()
    puzzle = LinkSolver(mat)
    puzzle.solve()
    print("--- %s seconds ---" % (time.time() - start_time))