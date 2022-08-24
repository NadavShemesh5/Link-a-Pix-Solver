import time
from board import Board
from board_solver import BoardSolver
from timetester import TimeTester
from scipy.io import loadmat
import numpy as np


class Analyzer:
    def __init__(self, solver):
        self.solver = solver

    def run_samples(self, contains_path: str):
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
                    results[file].append(self.run_sample(file))
        for key, value in results.items():
            print(f"{key}, avg:{np.average(value)}")

    def run_sample(self, filename: str):
        board = Board(loadmat(filename))
        solver = BoardSolver(board)
        analyzer = Analyzer(solver)
        analyzer.analyze()
        start_time = time.time()
        if solver.solve():
            runtime = time.time() - start_time
            print(f"--- solved in {runtime} seconds ---")
            # print details:
            # for key, value in TimeTester.TimesGlobal.items():
            #     print(f"{key}: {value}")
            print(f"DeepCopies: {TimeTester.DeepCopies}")
        else:
            print("--- failed to find a solution ---")
        return runtime

    def analyze(self, specific_sample: str = None, samples_contains: str = None, all_files: bool = False):
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
            self.run_sample(specific_sample)
        elif samples_contains:
            self.run_samples(samples_contains)
        elif all_files:
            self.run_samples('')
        else:
            print("Error! You need to choose at-least one file to analyze!")
