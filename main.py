import scipy.io
import time
from board import Board

if __name__ == '__main__':
    mat_data = scipy.io.loadmat('data_20_20_basketball.mat')
    board = Board(mat_data)
    start_time = time.time()
    board.calculate_all_paths()
    print(board.pretty_print())
    print("--- %s seconds ---" % (time.time() - start_time))