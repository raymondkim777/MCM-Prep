import csv
import argparse
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate


CSV_PATH = './data_chicks.csv'


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', action="store_true", help='plot figures')
    parser.add_argument('-d', action="store_true", help='(with plot enabled) plot deterministic model')
    parser.add_argument('-s', action="store_true", help='(with plot enabled) plot stochastic model')
    parser.add_argument('-a', action="store_true", help='(with plot enabled) plot average of stochastic model') 
    parser.add_argument('-t', type=int, default=1, help='number of trials for stochastic model')
    return parser.parse_args()


def load_csv():
    data = []
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile,delimiter=',')
        header = next(reader)  # reads and discards header
        for [year, rec, sur, pop] in reader:
            data.append([int(year), float(rec), float(sur), float(pop)])
    return data


def calculate_mean_sd(data):
    recruits = []
    survival = []
    for [_, rec, sur, _] in data:
        recruits.append(rec)
        survival.append(sur)
    mean_r, std_r = np.mean(recruits), np.std(recruits)
    mean_s, std_s = np.mean(survival), np.std(survival)
    return mean_r, std_r, mean_s, std_s


def print_stats(stats: tuple):
    mean_r, std_r, mean_s, std_s = stats
    headers = ["", "Recruitment", "Survival"]
    stat_table = [["Mean", mean_r, mean_s], ["St.D", std_r, std_s]]
    print(f"\nStatistics:")
    print(tabulate(stat_table, headers=headers, floatfmt=".2f"))
    print()


def plot_model(data: list, stats: tuple, det=False, sto=False, trials=1, avg=False):
    # x0 = 273.8
    # DET: x(n) = x(n - 1) * mean_s + mean_r
    # STO: x(n) = x(n - 1) * Normal(mean_s, std_s) + Normalize(mean_r, std_r)
    
    mean_r, std_r, mean_s, std_s = stats
    
    years = [sublist[0] for sublist in data]
    data_raw = [sublist[3] for sublist in data]
    plt.plot(years, data_raw, color='red')
    
    if det:
        data_det = [data[0][3]]  # initial pop
        for i in range(len(years) - 1):
            if det:
                data_det.append(data_det[-1] * mean_s + mean_r)
        plt.plot(years, data_det, color='blue')

    if sto:
        all_trials = []
        data_sum = [data[0][3] * trials] + [0 for i in range(len(years) - 1)]

        for t in range(trials):
            data_sto = [data[0][3]]  # initial pop
            for i in range(len(years) - 1):
                survive_rate = np.random.normal(mean_s, std_s)
                recruit_rate = np.random.normal(mean_r, std_r)

                new_pop = data_sto[-1] * survive_rate + recruit_rate
                data_sto.append(new_pop)
                data_sum[i + 1] += new_pop

            all_trials.append(data_sto)
            plt.plot(years, data_sto, color='grey', alpha=0.6/trials + 0.4)
        
        data_sum = [d / trials for d in data_sum]
        if avg:
            plt.plot(years, data_sum, color='black')
    plt.show()


if __name__ == "__main__":
    args = _parse_args()

    data = load_csv()
    stats = calculate_mean_sd(data)
    print_stats(stats)

    if args.plot:
        plot_model(
            data, 
            stats, 
            det=args.d, 
            sto=args.s, 
            trials=args.t,
            avg=args.a,
        )