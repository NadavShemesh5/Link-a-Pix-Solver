import time
import contstants
from board import Board
from board_solver import BoardSolver
from scipy.io import loadmat
import numpy as np
from timetester import TimeTester
import matplotlib.pyplot as plt
import pickle

categories = ["20_20", "data_32_32", "data_e_32_32", "data_e_40_40", "64_64", "128_128"]  # full test


# categories = ["20_20", "data_32_32"]  # test without linear step


def get_fixed_category_name(cat_name, row_down=False):
    c = cat_name
    addon = " common"
    if 'data_' in cat_name:
        c = c.replace('data_', '')
    if 'e_' in cat_name:
        c = c.replace('e_', '')
        addon = " non-fully filled"
    c = c.replace('_', ' x ')
    if row_down:
        c = c + "\n"
    return c + addon


def create_graphs_helper(time_groups, paths_groups):
    fixed_cats = [get_fixed_category_name(c) for c in categories]

    for i in range(len(time_groups)):
        times = time_groups[i]
        paths = paths_groups[i]
        # Logarithmic graph
        plt.xlabel('Feasible paths', fontsize=14, labelpad=15)
        plt.ylabel('Solving time (s)', fontsize=14, labelpad=10)
        plt.scatter(paths, times, s=10, label=categories[i])
        plt.yscale("log")
        plt.xscale("log")
    plt.legend(fixed_cats)
    plt.savefig('runtime_summary_graph.png', dpi=800, bbox_inches="tight")

    plt.clf()

    fig, ax = plt.subplots(figsize=(10, 10))

    x = np.arange(len(fixed_cats))  # the label locations
    width = 0.35  # the width of the bars

    # their bars
    row_avg = [1.11, 4.91, 21.48, 46.48, 80.93, 716.82]  # includes data_e versions
    # row_avg = [1.11, 4.91]  # does not include data_e versions
    if len(fixed_cats) != len(row_avg):
        print("The length of row_average and fixed_cats must be equal!")
        exit(1)
    rects1 = ax.bar(x - width / 2, row_avg, width)

    # our bars
    row_avg = [sum(ti) / len(ti) for ti in time_groups]
    rects2 = ax.bar(x + width / 2, [round(r, 2) for r in row_avg], width)

    # graph properties
    plt.xlabel('Categories', fontsize=14, labelpad=15)
    plt.ylabel('Solving time (s)', fontsize=14, labelpad=10)
    plt.yscale("log")
    ax.set_xticks(x, [get_fixed_category_name(c, row_down=True) for c in categories])
    ax.bar_label(rects1, padding=8)
    ax.bar_label(rects2, padding=8)
    plt.legend(["Article results", "Our results"])
    plt.savefig(f'runtime_comparison_graph_{contstants.USE_LINEAR_STEP}.png', dpi=800, bbox_inches="tight")

    plt.clf()
    paths_combined = [k for p in paths_groups if len(p) > 0 for k in p]
    times_combined = [k for p in time_groups if len(p) > 0 for k in p]
    b, m = np.polynomial.polynomial.polyfit(x=np.log(paths_combined), y=np.log(times_combined), deg=1)
    print(b, m)

    plt.clf()
    paths_combined = [379.2, 2345.0, 5134.5, 8327.7, 13043.2, 36665.0]
    times_combined = [1.11, 4.91, 21.48, 46.48, 80.93, 716.82]
    b, m = np.polynomial.polynomial.polyfit(x=np.log(paths_combined), y=np.log(times_combined), deg=1)
    print(b, m)


def create_graphs(time_results):
    time_groups = []
    paths_groups = []
    for cat in categories:
        times = [time_results[result] for result in time_results.keys() if cat in result]
        paths = [TimeTester.PathsNumber[result] for result in TimeTester.PathsNumber.keys() if
                 cat in result]
        time_groups.append(times)
        paths_groups.append(paths)
        if len(times) > 0:
            with open(f'{cat}_times.pickle', 'wb') as h1:
                pickle.dump(times, h1, protocol=pickle.HIGHEST_PROTOCOL)
            # with open(f'{cat}_paths.pickle', 'wb') as h2:
            #     pickle.dump(paths, h2, protocol=pickle.HIGHEST_PROTOCOL)
    create_graphs_helper(time_groups, paths_groups)


def run_samples(contains_path: str):
    from os import listdir
    from os.path import isfile, join
    path = './'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    test_iterations = 1
    time_results = {}
    for i in range(test_iterations):
        for file in files:
            if isinstance(contains_path, str):
                if contains_path in file and ".mat" in file:
                    time_results[file] = run_sample(file)
            else:
                for p in contains_path:
                    if p in file and ".mat" in file:
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


def analyze(specific_sample: str = None, samples_contains=None, all_files: bool = False):
    """
    Analyzes a specific sample, category, or all the available files

    Parameters
    ----------
    specific_sample : str, optional
        A specific sample to analyze, like: 'data_32_32_kangaroo.mat'

    samples_contains : str or array, optional
        Analyzes only samples that contain this text (or one of the texts in the list),
        like: 'data_20' or ['data_32', 'data_20']

    all_files : bool, optional
        Choose if to analyze all the samples

    """
    if specific_sample:
        run_sample(filename=specific_sample)
    elif samples_contains:
        run_samples(samples_contains)
    elif all_files:
        run_samples('')
    else:
        print("Error! You need to choose at-least one file to analyze!")


def load():
    analyze(all_files=True,
            samples_contains=None,
            specific_sample=None)


if __name__ == '__main__':
    if contstants.CREATE_GRAPHS:
        fail = False
        t_groups = []
        p_groups = []
        for category in categories:
            try:
                with open(f'{category}_times.pickle', 'rb') as f1:
                    t = pickle.load(f1)
                    t_groups.append(t)
                with open(f'{category}_paths.pickle', 'rb') as f2:
                    g = pickle.load(f2)
                    p_groups.append(g)
            except (OSError, IOError) as e:
                fail = True
                break
        if fail:
            print("PICKLE DOESN'T EXIST!")
            load()
        else:
            print("all found - create graphs!!")
            create_graphs_helper(t_groups, p_groups)
    else:
        load()
