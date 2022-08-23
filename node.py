from sty import fg, bg, ef, rs
from contstants import PRINT_SHOW_LENGTHS


class Node:
    # Should show lengths in the final printout
    def __init__(self, x, y, color, length='  ', is_clue=False):
        self.x, self.y = x, y
        self.color = color
        self.length = length
        self.is_clue = is_clue

    def printy(self, num: str = '  '):
        return bg(int(self.color + 1)) + num + rs.all

    def __repr__(self):
        return self.printy(str(self.length).zfill(2) if PRINT_SHOW_LENGTHS else '  ')
