import argparse
import math
import random
import numpy as np
import tabulate
# from scipy.stats import poisson

def _parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--n', type=int, default=50, help='number of trials to run model')
	parser.add_argument('--t', type=int, default=120, help='number of months')
	parser.add_argument('--tm', type=int, default=30, help='number of days in a month')
	parser.add_argument('--fire', type=int, default=4, help='average days in a month dragon breathes fire')
	parser.add_argument('--r', type=float, default=3, help='average yearly growth rate of dragon mass')
	parser.add_argument('--m0', type=float, default=10, help='initial dragon mass')
	# parser.add_argument('--regional', action='store_true', help='runs regional model instead of basic model')
	return parser.parse_args()


def calculate_monthly_food(
		cur_mass, 	# current dragon mass
		d = 30,     # days in a month
		lam = 4,    # average number of fire days per month
	):
	fire_days = np.random.poisson(lam)
	return (d + fire_days) * 0.2209 * np.power(cur_mass, 0.75)


def dragon_model(
		n = 50,     # trial number
		t = 120,    # number of months to run model
		d = 30,     # days in a month
		lam = 4,    # average number of fire days per month
		r = 3,      # average yearly mass growth rate
		m_0 = 10,    # initial dragon mass
	):

	trials = []
	
	all_mass_list = []
	all_food_list = []
	
	# run trials
	for trial in range(n):
		trial_mass_list = []
		trial_food_list = []
		
		# initalize mass
		cur_mass = m_0
		
		for month in range(t):
			# compute food based on current mass
			cur_food = calculate_monthly_food(cur_mass, d=d, lam=lam)

			# append mass/food to trial list
			trial_mass_list.append(cur_mass)
			trial_food_list.append(cur_food)

			# update mass
			cur_mass *= np.power(r, 1/12)
		
		trial_mass_list.append(cur_mass)
		trial_food_list.append(0)

		# append trials
		all_mass_list.append(trial_mass_list)
		all_food_list.append(trial_food_list)

		if trial == 0:
			trials.append([None, "Mass"] + trial_mass_list)
		trials.append([trial + 1, "Food"] + trial_food_list)
	
	headers = ['Trial', 'Type'] + [i + 1 for i in range(t + 1)]
	with open('results.txt', 'w', encoding='utf-8') as f:
		f.write(tabulate.tabulate(trials, headers=headers, floatfmt=".2f"))


if __name__ == "__main__":
	random.seed(42)

	args = _parse_args()
	dragon_model(
		n = args.n,         # number of trials
		t = args.t,         # number of months to run model
		d = args.tm,        # days in a month
		lam = args.fire,    # average number of fire days per month
		r = args.r,         # average yearly mass growth rate
		m_0 = args.m0,       # initial dragon mass
	)