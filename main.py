import scipy.io
import time
from board_solver import BoardSolver
from board import Board

if __name__ == '__main__':
    mat_data = scipy.io.loadmat('data_20_20_basketball.mat')
    board = Board(mat_data)
    solver = BoardSolver(board)
    start_time = time.time()
    solver.solve()
    print("--- %s seconds ---" % (time.time() - start_time))