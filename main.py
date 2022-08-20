import scipy.io
import time
from board_solver import BoardSolver
from board import Board

if __name__ == '__main__':
    mat_data = scipy.io.loadmat('data_20_20_basketball.mat')
    board = Board(mat_data)
    solver = BoardSolver(board)
    start_time = time.time()
    if solver.solve():
        print(f"--- solved in {time.time() - start_time} seconds ---")
    else:
        print("--- failed to find a solution ---")
    print(board.Counter)
