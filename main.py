import scipy.io
import time
from board_solver import BoardSolver
from board import Board
import numpy as np

from timetester import TimeTester


def test_all(contains_path):
    from os import listdir
    from os.path import isfile, join
    path = './'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    test_iterations = 1
    results = {}
    for i in range(test_iterations):
        for file in files:
            if contains_path in file:
                if file not in results:
                    results[file] = []
                results[file].append(run_sample(file))

    for key, value in results.items():
        print(f"{key}, avg:{np.average(value)}")


def run_sample(filename):
    mat_data = scipy.io.loadmat(filename)
    board = Board(mat_data)
    solver = BoardSolver(board)
    start_time = time.time()
    if solver.solve():
        runtime = time.time() - start_time
        print(f"--- solved in {runtime} seconds ---")
        # print details:
        for key, value in TimeTester.TimesGlobal.items():
            print(f"{key}: {value}")
        print(f"DeepCopies: {TimeTester.DeepCopies}")

    else:
        print("--- failed to find a solution ---")
    return runtime


if __name__ == '__main__':
    #run_sample('data_32_32_kangaroo.mat')
    #run_sample("data_32_32_damura.mat")
    test_all("data_32")
