import argparse
import scipy.io
from copy import deepcopy
import numpy as np
import time


class Link:
    def __init__(self, init_dist, curr_position):
        self.init_dist = init_dist
        self.curr_position = curr_position
        self.possible_paths = []
        self.heuristic_value = -1

    def __lt__(self, other):
        return self.heuristic_value < other.heuristic_value


class Board:
    def __init__(self, data, width, height):
        self.width = width
        self.height = height
        self.data = data

    def search_helper(self, curr_position, dist_left, init_dist, path, paths):
        if dist_left < 1:
            return

        x, y = curr_position
        if self.data[x, y] != 0 and \
                dist_left == 1 and \
                self.data[x, y].init_dist == init_dist:
            paths.append(path + [curr_position])
            return

        if self.data[x, y] != 0:
            return

        if x != self.width - 1 and self.data[x + 1, y] != 1 and (x + 1, y) not in path:
            self.search_helper((x + 1, y), dist_left - 1, init_dist, path + [curr_position], paths)
        if y != self.height - 1 and self.data[x, y + 1] != 1 and (x, y + 1) not in path:
            self.search_helper((x, y + 1), dist_left - 1, init_dist, path + [curr_position], paths)
        if x != 0 and self.data[x - 1, y] != 1 and (x - 1, y) not in path:
            self.search_helper((x - 1, y), dist_left - 1, init_dist, path + [curr_position], paths)
        if y != 0 and self.data[x, y - 1] != 1 and (x, y - 1) not in path:
            self.search_helper((x, y - 1), dist_left - 1, init_dist, path + [curr_position], paths)

    def find_all_paths(self, link):
        ret = []
        x, y = link.curr_position
        if x != self.width - 1 and self.data[x + 1, y] != 1:
            self.search_helper((x + 1, y), link.init_dist - 1, link.init_dist, [(x, y)], ret)
        if y != self.height - 1 and self.data[x, y + 1] != 1:
            self.search_helper((x, y + 1), link.init_dist - 1, link.init_dist, [(x, y)], ret)
        if x != 0 and self.data[x - 1, y] != 1:
            self.search_helper((x - 1, y), link.init_dist - 1, link.init_dist, [(x, y)], ret)
        if y != 0 and self.data[x, y - 1] != 1:
            self.search_helper((x, y - 1), link.init_dist - 1, link.init_dist, [(x, y)], ret)
        return ret

    def fill_path(self, path, link):
        for (x, y) in path:
            # self.data[x, y] = link.init_dist
            self.data[x, y] = 1

    def __str__(self):
        ret = ""
        for row in self.data:
            for item in row:
                if item != 0:
                    ret += chr(9608) + chr(9608)
                else:
                    ret += "  "
                # if item != 0:
                #     if type(item) == int:
                #         ret += str(item)
                #     else:
                #         ret += str(item.init_dist % 10)
                # else:
                #     ret += " "
            ret += "\n"
        return ret


class LinkSolver:
    def __init__(self, data: list):
        self.links = []
        width = len(data)
        height = len(data[0])
        curr_data = np.zeros((width, height), dtype=Link)
        for row in range(width):
            for col in range(height):
                curr_val = data[row][col]
                if curr_val != 0:
                    curr_data[row, col] = 1
                    if curr_val > 2:
                        curr_link = Link(curr_val, (row, col))
                        curr_data[row, col] = curr_link
                        self.links.append(curr_link)
        self.board = Board(curr_data, width, height)
        for link in self.links:
            paths = self.board.find_all_paths(link)
            link.possible_paths = paths
            link.heuristic_value = len(link.possible_paths)
        self.links.sort()

    def evaluate_links_and_sort(self, path):
        modified = False
        for link in self.links:
            for new_position in path:
                if abs(link.curr_position[0] - new_position[0]) + \
                        abs(link.curr_position[1] - new_position[1]) <= link.init_dist:
                    link.possible_paths[:] = [old_path for old_path in link.possible_paths
                                              if new_position not in old_path]
                    if not link.possible_paths:
                        return False
                    link.heuristic_value = len(link.possible_paths)
                    if link.heuristic_value != len(link.possible_paths):
                        modified = True
        if modified:
            self.links.sort()
        return True

    def solve(self):
        if not self.links:
            print(self.board)
            return True

        curr_link = self.links.pop(0)
        possible_paths = curr_link.possible_paths

        if len(possible_paths) == 0:
            return False

        elif len(possible_paths) == 1:
            self.links.remove(self.board.data[possible_paths[0][-1]])
            self.board.fill_path(possible_paths[0], curr_link)
            if not self.evaluate_links_and_sort(possible_paths[0]):
                return False
            return self.solve()

        else:
            # modified = False
            # for link in self.links:
            #     link.possible_paths[:] = [old_path for old_path in link.possible_paths if
            #                               all(self.board.data[position] != 1 for position in old_path)]
            #     if not link.possible_paths:
            #         return False
            #     if link.heuristic_value != len(link.possible_paths):
            #         modified = True
            #     link.heuristic_value = len(link.possible_paths)
            # if modified:
            #     self.links.sort()
            for path in possible_paths:
                new_self = deepcopy(self)
                new_self.links.remove(new_self.board.data[path[-1]])
                new_self.board.fill_path(path, curr_link)
                if not new_self.evaluate_links_and_sort(path):
                    continue
                if new_self.solve():
                    return True

        return False

    def __str__(self):
        return self.board.__str__()


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-i", "--puzzle_data", type=int, required=True)
    # args = parser.parse_args()
    #
    # puzzle = LinkSolver(args.puzzle_data)
    # mat = scipy.io.loadmat('data_32_32_kangaroo.mat')
    start_time = time.time()
    for i in range(10):
        puzzle = LinkSolver([[0, 0, 0, 4, 10, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0],
                             [0, 0, 1, 0, 0, 4, 0, 0, 0, 5, 0, 0, 0, 5, 0],
                             [0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 6, 0, 0, 0],
                             [0, 0, 0, 0, 0, 5, 0, 0, 0, 6, 0, 1, 0, 0, 0],
                             [0, 0, 0, 0, 0, 10, 0, 0, 0, 1, 0, 0, 3, 0, 0],
                             [0, 0, 0, 8, 0, 5, 0, 4, 0, 0, 3, 0, 0, 0, 0],
                             [0, 0, 1, 0, 0, 0, 0, 0, 8, 5, 0, 0, 3, 0, 5],
                             [0, 9, 0, 0, 0, 0, 5, 0, 0, 0, 3, 0, 0, 5, 0],
                             [14, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0],
                             [0, 0, 0, 0, 0, 0, 8, 0, 0, 3, 0, 3, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 0],
                             [0, 0, 0, 5, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [4, 4, 0, 14, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0],
                             [3, 0, 3, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0]])
        puzzle.solve()
    print("--- %s seconds ---" % ((time.time() - start_time)/10))
    # print(puzzle)
