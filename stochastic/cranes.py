from tabulate import tabulate
import argparse
from math import comb
from numpy.random import normal, uniform, binomial


def display_histogram(data, num_bins=8):
    pass


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, default="both", help='demo/env/both (demographic + environmental)')
    parser.add_argument('-t', '--trials', type=int, default=20, help='number of trials to run')
    parser.add_argument('-n', '--years', type=int, default=5, help='number of years to run')
    parser.add_argument('--pop0', type=int, default=100, help='initial crane population')
    parser.add_argument('--mbirth', type=float, default=0.5, help='crane birth rate mean')
    parser.add_argument('--sbirth', type=float, default=0.03, help='crane birth rate standard deviation')
    parser.add_argument('--mdeath', type=float, default=0.1, help='crane death rate mean')
    parser.add_argument('--sdeath', type=float, default=0.08, help='crane death rate standard deviation')
    parser.add_argument('--catrate', type=float, default=0.04, help='catastrophe occurrence rate')
    parser.add_argument('--cbirth', type=float, default=-0.4, help='catastrophe effect on birth rate')
    parser.add_argument('--cdeath', type=float, default=0.25, help='catastrophe effect on death rate')
    
    return parser.parse_args()


def crane_model_demo(
        trial_cnt: int, 
        years: int, 
        init_pop: int,
        birth_mean: float, 
        birth_sd: float, 
        death_mean: float,
        death_sd: float,
    ):
    # record each trial data
    trials = []
    
    for i in range(trial_cnt):
        # initialize population
        pop = init_pop

        # record the population at each year
        yearly_pop = [init_pop]

        for year in range(1, years + 1):
            # sample from normal distribution (mean, sd) for regular birth and death rate
            birth_rate = normal(birth_mean, birth_sd)
            death_rate = normal(death_mean, death_sd)

            # calculate growth rate
            growth_rate = birth_rate - death_rate
            
            # calculate new population
            pop *= (1 + growth_rate)
            yearly_pop.append(pop)
        
        trials.append([i + 1] + yearly_pop)     # trial #, initial, years....

    # print output
    with open("results_demo.txt", "w", encoding="utf-8") as f:
        headers = ["Run", "Initial"] + list(range(1, years + 1))
        f.write(tabulate(trials, headers=headers, floatfmt=".2f"))


def crane_model_env(
        trial_cnt: int, 
        years: int, 
        cat_rate: float, 
    ):
    # catastrophe frequencies
    freqs = {cnt: 0 for cnt in range(years + 1)}
    probs = {cnt: comb(years, cnt) * (cat_rate ** cnt) * ((1 - cat_rate) ** (years - cnt)) for cnt in range(years + 1)}
    
    for i in range(trial_cnt):
        # catastrophe count
        cat_cnt = 0

        # simulate catastrophe counts
        for year in range(years):
            cat_cnt += uniform(low=0.0, high=1.0) <= cat_rate      # boolean
        
        # add catastrophe frequency
        freqs[cat_cnt] += 1
    
    headers = ["Cat #", "Freq.", "Rel. Freq", "Probability"]
    output = [[
            cnt, 
            freqs[cnt], 
            f"{freqs[cnt] / trial_cnt * 100:.2f}%", 
            f"{probs[cnt] * 100:.2f}%"
        ] for cnt in range(years + 1)
    ]

    # print output
    with open("results_env.txt", "w", encoding="utf-8") as f:
        f.write(f"Total Trials: {trial_cnt}\n\n")
        f.write(tabulate(output, headers=headers))


def crane_model(
        trial_cnt: int, 
        years: int, 
        init_pop: int,
        birth_mean: float, 
        birth_sd: float, 
        death_mean: float,
        death_sd: float,
        cat_rate: float, 
        cat_birth: float, 
        cat_death: float,
    ):
    # record each trial data
    trials = []
    
    for i in range(trial_cnt):
        # initialize population
        pop = init_pop

        # record the population at each year
        yearly_pop = [init_pop]

        # catastrophe count
        cat_cnt = 0

        for year in range(1, years + 1):
            # sample from normal distribution (mean, sd) for regular birth and death rate
            birth_rate = normal(birth_mean, birth_sd)
            death_rate = normal(death_mean, death_sd)

            # sample catastrophe
            cat_occur = uniform(low=0.0, high=1.0) <= cat_rate      # boolean
            
            if cat_occur:
                cat_cnt += 1

                # calculate modified birth rate
                birth_rate *= 1 + cat_birth
                death_rate *= 1 + cat_death

            # calculate growth rate
            growth_rate = birth_rate - death_rate
            
            # calculate new population
            pop *= (1 + growth_rate)
            yearly_pop.append(f"{pop:.2f}") if not cat_occur else yearly_pop.append(f"{pop:.2f} (CAT)")
        
        trials.append([i + 1] + yearly_pop + [cat_cnt])     # trial #, initial, years....

    # print output
    with open("results_both.txt", "w", encoding="utf-8") as f:
        headers = ["Run", "Initial"] + list(range(1, years + 1)) + ["Cat #"]
        f.write(tabulate(trials, headers=headers, floatfmt=".2f"))


if __name__ == "__main__":
    args = _parse_args()

    if args.model == 'demo':
        crane_model_demo(
            trial_cnt=args.trials, 
            years= args.years, 
            init_pop=args.pop0,
            birth_mean=args.mbirth, 
            birth_sd=args.sbirth, 
            death_mean=args.mdeath,
            death_sd=args.sdeath,
        )
    
    elif args.model == 'env':
        crane_model_env(
            trial_cnt=args.trials, 
            years= args.years, 
            cat_rate=args.catrate, 
        )

    elif args.model == 'both':
        crane_model(
            trial_cnt=args.trials, 
            years= args.years, 
            init_pop=args.pop0,
            birth_mean=args.mbirth, 
            birth_sd=args.sbirth, 
            death_mean=args.mdeath,
            death_sd=args.sdeath,
            cat_rate=args.catrate, 
            cat_birth=args.cbirth, 
            cat_death=args.cdeath,
        )
    
    else:
        raise ValueError('Incorrect --model argument input')