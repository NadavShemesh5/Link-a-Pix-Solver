from node import Node


class Clue(Node):
    def __init__(self, x: int, y: int, length: int, color: int):
        super().__init__(x, y, color)
        self.length = length
        self.paths = []

    def calculate_paths(self, board):
        self.paths = []
        #print(f"---pos:({self.x},{self.y}), len:{self.length}---")
        self.calculate_paths_helper(self.x, self.y, self.length, self.color, board, [], first_call=True)
        #print(len(self.paths))
        # for path in self.paths:
        #     print(path)

    def calculate_paths_helper(self, x, y, length, color, board, path, first_call=False):
        def reached_dest(value):
            return length == 1 and value != 0 and value.color == color and self.length == value.length

        # Check if length or position invalid, or already visited node
        if length < 1 or not board.is_valid_position(x, y) or (x, y) in path:
            return

        # Check if we reached destination
        if reached_dest(board.get(x, y)):
            self.paths.append(path + [(x, y)])
            return

        # Check if we hit a clue with wrong length
        if not first_call and (length == 1 or board.get(x, y) != 0):
            return

        self.calculate_paths_helper(x + 1, y, length - 1, color, board, path + [(x, y)])
        self.calculate_paths_helper(x - 1, y, length - 1, color, board, path + [(x, y)])
        self.calculate_paths_helper(x, y + 1, length - 1, color, board, path + [(x, y)])
        self.calculate_paths_helper(x, y - 1, length - 1, color, board, path + [(x, y)])

    def __repr__(self):
        return super().printy(str(self.length).zfill(2))
