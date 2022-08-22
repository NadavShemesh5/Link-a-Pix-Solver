from contstants import PRINT_SHOW_LENGTHS


class Node:

    # Should show lengths in the final printout
    def __init__(self, x, y, color, length='  ', is_clue=False):
        self.x, self.y = x, y
        self.color = color
        self.length = length
        self.is_clue = is_clue

    def printy(self, num: str = '  '):
        def get_color_coded_str(i, s: str):
            return f"\033[4{i + 1}m{s}\033[0m".format(i + 1, s)

        return get_color_coded_str(self.color, num)

    def __repr__(self):
        return self.printy(str(self.length).zfill(2) if PRINT_SHOW_LENGTHS else '  ')