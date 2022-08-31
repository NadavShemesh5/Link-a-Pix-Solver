import time
import settings
from board import Board
from board_solver import BoardSolver
from scipy.io import loadmat
import numpy as np
from timetester import TimeTester
import matplotlib.pyplot as plt
import pickle
import os

categories = ["20_20", "data_32_32", "data_e_32_32", "data_e_40_40", "64_64", "128_128"]  # full test


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

    # for k in range(len(time_groups)):
    #     for i in reversed(range(len(paths_groups[k].copy()))):
    #         print(paths_groups[k][i])
    #         if paths_groups[k][i] == 0:
    #             del time_groups[k][i]
    #             #del fixed_cats[i]
    #             del paths_groups[k][i]

    for i in range(len(time_groups)):
        times = time_groups[i]
        paths = paths_groups[i]
        # Logarithmic graph
        plt.xlabel('Feasible paths', fontsize=14, labelpad=15)
        plt.ylabel('Solving time (s)', fontsize=14, labelpad=10)
        print(times, paths)
        plt.scatter(paths, times, s=10, label=categories[i])
        plt.yscale("log")
        plt.xscale("log")

        print(np.average(paths))
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
    plt.savefig(f'runtime_comparison_graph_{settings.USE_LINEAR_STEP}.png', dpi=800, bbox_inches="tight")

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
    if not len(files) > 0:
        file_error()
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
    if settings.PRINT_SPECIFIC_TIME_MEASURES:
        print(f"\nRuntime summary:")
        print("----------------------------------------------------")
        for key, value in time_results.items():
            print(f"{key}, avg:{np.average(value)}")
    if settings.CREATE_GRAPHS:
        create_graphs(time_results)


def file_error():
    print("No file or category was found with the given name, make sure to type the right name")
    exit(1)


def run_sample(filename: str):
    TimeTester.CurrentSample = filename
    print(f"\n --- Now solving {filename}:")
    if not os.path.isfile(filename):
        file_error()
    board = Board(loadmat(filename))
    solver = BoardSolver(board)
    start_time = time.time()
    if solver.solve():
        runtime = time.time() - start_time
        if settings.PRINT_SPECIFIC_TIME_MEASURES:
            for key, value in TimeTester.TimesGlobal.items():
                print(f"{key}: {value}")
        if settings.CHECK_NUM_OF_PATHS:
            if filename in TimeTester.PathsNumber:
                print(f"{filename}                | total_paths:{TimeTester.PathsNumber[filename]}")
            # for key, value in TimeTester.PathsNumber.items():
            #     print(f"{key}                | total_paths:{value}")
        if settings.PRINT_SPECIFIC_TIME_MEASURES:
            print(f"--- solved in {runtime} seconds --- \n")
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


def load(options):
    run = options.solve
    if run == 'all':
        analyze(all_files=True,
                samples_contains=False,
                specific_sample=None)
    elif run == 'category':
        category_name = options.name
        if not category_name:
            print("Error! you need to state a category name to analyze!")
            exit(1)
        analyze(all_files=False,
                samples_contains=category_name,
                specific_sample=None)
    elif run == 'sample':
        sample_name = options.name
        if not sample_name:
            print("Error! you need to state a sample name to analyze!")
            exit(1)
        if '.mat' not in sample_name:
            sample_name += '.mat'
        analyze(all_files=False,
                samples_contains=False,
                specific_sample=sample_name)
    else:
        print("Error! You need to choose at-least one type - 'all', 'category', or 'sample'")
        exit(1)


def main():
    from optparse import OptionParser

    usage_str = """
            USAGE:      python main.py <options>
            EXAMPLES:  (1) python main.py --solve all
                          - Solves all of the available samples
                       (2) python main.py --solve all --times --clues
                          - Solves all of the available samples, prints the runtime summary and shows the clues in the printed solution   
                       (3) python main.py --solve sample --name data_32_32_samurai
                          - Solves a specific sample with the given name
                       (4) python main.py --solve category --name 20_20 --print False
                          - Solves a specific category of 20_20 boards, without printing the game board results
            """
    parser = OptionParser(usage_str)
    parser.add_option('-g', '--graphs', dest='graphs',
                      help='Indicates whether to create runtime graphs',
                      default=False, action="store_true")
    parser.add_option('-p', '--print', dest='print',
                      help='Indicates whether to print the complete game board',
                      default=True, action="store_true")
    parser.add_option('-c', '--clues', dest='clues',
                      help='Indicates whether to show the clues numbers in the game board',
                      default=False, action="store_true")
    parser.add_option('-t', '--times', dest='times',
                      help='Indicates whether to show specific time measures of different components in each sample',
                      default=False, action="store_true")
    parser.add_option('-l', '--linear-step', dest='linear',
                      help='Indicates whether to include the linear programming step or not',
                      default=True, action="store_true")
    parser.add_option('-s', '--solve', dest='solve',
                      help='Choose if to run all samples, a category of samples, or a specific sample')
    parser.add_option('-n', '--name', dest='name',
                      help='Indicate the name of the specific sample or category to analyze')

    # Parse the arguments
    options, cover_points = parser.parse_args()

    if not options.solve:
        parser.error('solve type was not given, please state -s [sample|category|all]')

    # Initialize settings
    settings.CREATE_GRAPHS = options.graphs
    settings.PRINT_BOARD = options.print
    settings.PRINT_SHOW_LENGTHS = options.clues
    settings.PRINT_SPECIFIC_TIME_MEASURES = options.times
    settings.USE_LINEAR_STEP = options.linear

    if settings.CREATE_GRAPHS:
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
            # print("PICKLE DOESN'T EXIST!")
            load(options)
        else:
            # print("all found - create graphs!!")
            create_graphs_helper(t_groups, p_groups)
    else:
        load(options)


if __name__ == '__main__':
    main()
