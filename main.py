import time
import contstants
from board import Board
from board_solver import BoardSolver
from scipy.io import loadmat
import numpy as np
from timetester import TimeTester
import matplotlib.pyplot as plt



def create_graphs(time_results):

    categories = ["20_20", "32_32", "40_40", "64_64", "128_128"]
    for cat in categories:
        group_times = [time_results[result] for result in time_results.keys() if cat in result]
        group_paths = [TimeTester.PathsNumber[result] for result in TimeTester.PathsNumber.keys() if
                       cat in result]
        # Logarithmic graph
        plt.xlabel('Feasible paths', fontsize=14, labelpad=15)
        plt.ylabel('Solving time (s)', fontsize=14, labelpad=10)
        plt.scatter(group_paths, group_times, s=10, label=cat)
        plt.yscale("log")
        plt.xscale("log")
    plt.legend([c.replace('_', ' x ') for c in categories])
    plt.savefig('foo.png', dpi=800, bbox_inches="tight")


def run_samples(contains_path: str):
    from os import listdir
    from os.path import isfile, join
    path = './'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    test_iterations = 1
    time_results = {}
    for i in range(test_iterations):
        for file in files:
            if contains_path in file:
                time_results[file] = run_sample(file)
    for key, value in time_results.items():
        print(f"{key}, avg:{np.average(value)}")
    if contstants.CREATE_GRAPHS:
        create_graphs(time_results)


def run_sample(filename: str):
    TimeTester.CurrentSample = filename
    print(f"--- now solving {filename} ---")
    board = Board(loadmat(filename))
    solver = BoardSolver(board)
    start_time = time.time()
    if solver.solve():
        runtime = time.time() - start_time
        if contstants.PRINT_SPECIFIC_TIME_MEASURES:
            for key, value in TimeTester.TimesGlobal.items():
                print(f"{key}: {value}")
        if contstants.CHECK_NUM_OF_PATHS:
            if filename in TimeTester.PathsNumber:
                print(f"{filename}                | total_paths:{TimeTester.PathsNumber[filename]}")
            # for key, value in TimeTester.PathsNumber.items():
            #     print(f"{key}                | total_paths:{value}")
        print(f"--- solved in {runtime} seconds ---")
        return runtime
    else:
        print("--- failed to find a solution ---")
        return -1


def analyze(specific_sample: str = None, samples_contains: str = None, all_files: bool = False):
    """
    Analyzes a specific sample, category, or all the available files

    Parameters
    ----------
    specific_sample : str, optional
        A specific sample to analyze, like: 'data_32_32_kangaroo.mat'

    samples_contains : str, optional
        Analyzes only samples that contain this text, like: 'data_20' or 'data_32'

    all_files : bool, optional
        Choose if to analyze all the samples

    """
    if specific_sample:
        run_sample(filename=specific_sample)
    elif samples_contains:
        run_samples(samples_contains)
    elif all_files:
        run_samples('.mat')
    else:
        print("Error! You need to choose at-least one file to analyze!")


if __name__ == '__main__':
    analyze(all_files=True,
            samples_contains=None,
            specific_sample=None)
