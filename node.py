class Node:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color

    def printy(self, num: str = '  '):
        def get_color_coded_str(i, s: str):
            return "\033[4{}m{}\033[0m".format(i + 1, s)
        return get_color_coded_str(self.color, num)

    def __repr__(self):
        return self.printy()
