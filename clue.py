from node import Node
import copy


class Clue(Node):
    def __init__(self, x: int, y: int, length: int, color: int):
        super().__init__(x=x, y=y, color=color, length=length)
        self.paths = None
        self.general_paths_dicts = None
        self.paths_dicts = None


    def calculate_paths(self, board):
        self.paths = []
        self.calculate_paths_helper(self.x, self.y, self.length, self.color, board, [], first_call=True)

        # Initialize path dictionaries
        self.general_paths_dicts = {}
        self.paths_dicts = []
        for i in range(len(self.paths)):
            self.paths_dicts.append({})
            for p in self.paths[i]:
                self.paths_dicts[i][p] = self.paths[i]
                self.general_paths_dicts[p] = True
        return self.paths

    def calculate_paths_helper(self, x, y, length, color, board, path, first_call=False):
        # Check if length or position invalid, or already visited node
        if length < 1 or not board.is_valid_position(x, y) or (x, y) in path:
            return

        board_val = board.state[x, y]
        # Check if we reached destination
        if length == 1 and isinstance(board_val, Clue) and board_val.color == color and self.length == board_val.length:
            self.paths.append(path + [(x, y)])
            return

        # Check if we hit a clue with wrong length
        if not first_call and (length == 1 or board_val != 0):
            return

        self.calculate_paths_helper(x + 1, y, length - 1, color, board, path + [(x, y)])
        self.calculate_paths_helper(x - 1, y, length - 1, color, board, path + [(x, y)])
        self.calculate_paths_helper(x, y + 1, length - 1, color, board, path + [(x, y)])
        self.calculate_paths_helper(x, y - 1, length - 1, color, board, path + [(x, y)])

    def sort_value(self):
        return len(self.paths)

    def __repr__(self):
        return super().printy(str(self.length).zfill(2))

    def __lt__(self, other):
        if self.sort_value() == other.sort_value():
            return self.length > other.length
        return self.sort_value() < other.sort_value()

    def __gt__(self, other):
        return False

    def __eq__(self, other):
        return isinstance(other, Node) and self.x == other.x and self.y == other.y

    def __deepcopy__(self, memo={}):
        new_clue = Clue(self.x, self.y, self.length, self.color)
        new_clue.paths = self.paths.copy()
        new_clue.general_paths_dicts = self.general_paths_dicts.copy()
        new_clue.paths_dicts = self.paths_dicts.copy()
        return new_clue

    # def __hash__(self):
    #     return int((self.x + self.y + self.length + self.color) % 10000)
