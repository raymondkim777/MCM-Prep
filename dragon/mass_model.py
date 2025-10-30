import argparse
import random
import numpy as np
import tabulate
# from scipy.stats import poisson


CAL_COEFF = 0.2209
CAL_PER_KG = 5000
MAX_KG = 8000


def _parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--n', type=int, default=50, help='number of trials to run model')
	parser.add_argument('--t', type=int, default=120, help='number of months')
	parser.add_argument('--tm', type=int, default=30, help='number of days in a month')
	parser.add_argument('--fire', type=int, default=4, help='average days in a month dragon breathes fire')
	parser.add_argument('--r', type=float, default=3, help='average yearly growth rate of dragon mass')
	parser.add_argument('--f', type=float, default=0.5, help='average proportion of food to feed dragon (0~1)')
	parser.add_argument('--m0', type=float, default=10, help='initial dragon mass')
	parser.add_argument('--phase2', action="store_true")
	# parser.add_argument('--regional', action='store_true', help='runs regional model instead of basic model')
	return parser.parse_args()


def calculate_rer(cur_mass):
	return 70 * np.power(cur_mass, 0.75)


def calculate_monthly_food(
		cur_mass, 	# current dragon mass
		food_prop = 0.5,	# average proportion of food to feed dragon (0~1)
		d = 30,     # days in a month
		lam = 4,    # average number of fire days per month
	):
	# Here, food_prop = 0 means dragon is fed rer (minimum calories to survive) --> assumed to not grow

	fire_days = np.random.poisson(lam)
	cur_rer = (d + fire_days) * calculate_rer(cur_mass)		# rer (cal) for cur month
	min_food = cur_rer / CAL_PER_KG  # kg
	max_food = (d + fire_days) * CAL_COEFF * np.power(cur_mass, 0.75)  # kg
	new_food = min_food + food_prop * (max_food - min_food)
	return new_food, fire_days


def mass_model(
		n = 50,     # trial number
		t = 120,    # number of months to run model
		d = 30,     # days in a month
		lam = 4,    # average number of fire days per month
		r = 3,      # average yearly mass growth rate
		f = 0.5,	# average proportion of food to feed dragon (0~1)
		m_0 = 10,   # initial dragon mass
		phase2 = False,
	):

	trials = []
	
	all_mass_list = []
	all_food_list = []
	all_fire_list = []
	
	# run trials
	for trial in range(n):
		trial_mass_list = []
		trial_food_list = []
		trial_fire_list = []
		
		# initalize mass
		cur_mass = m_0
		
		for month in range(t):
			food_prop = f
			if not phase2 and cur_mass >= MAX_KG:
				# cap dragon mass
				food_prop = 0 
			cur_food, cur_fire = calculate_monthly_food(cur_mass, food_prop=food_prop, d=d, lam=lam)

			# append mass/food to trial list
			trial_mass_list.append(cur_mass)
			trial_food_list.append(cur_food)
			trial_fire_list.append(cur_fire)

			# update mass based on food_prop
			mass_growth = 1 + food_prop * (np.power(r, 1/12) - 1)
			cur_mass *= mass_growth
		
		trial_mass_list.append(cur_mass)
		trial_food_list.append(0)
		trial_fire_list.append(0)

		# append trials
		all_mass_list.append(trial_mass_list)
		all_food_list.append(trial_food_list)
		all_fire_list.append(trial_fire_list)

		if trial == 0:
			trials.append([None, "Mass"] + [f"{mass_val:.2f}" for mass_val in trial_mass_list])
		trials.append([trial + 1, "Food\nFire"] + [f"{trial_food_list[i]:.2f}\n{int(trial_fire_list[i])}" for i in range(len(trial_food_list))])
		# trials.append(["", "Fire"] +  trial_fire_list)
	
	headers = ['Trial', 'Type'] + [i + 1 for i in range(t + 1)]
	with open('mass_results.txt', 'w', encoding='utf-8') as f:
		f.write(tabulate.tabulate(trials, headers=headers, floatfmt=".2f", tablefmt='rounded_grid'))


if __name__ == "__main__":
	np.random.seed(42)

	args = _parse_args()
	mass_model(
		n = args.n,         # number of trials
		t = args.t,         # number of months to run model
		d = args.tm,        # days in a month
		lam = args.fire,    # average number of fire days per month
		r = args.r,         # average yearly mass growth rate
		f = args.f,
		m_0 = args.m0,       # initial dragon mass
		phase2 = args.phase2,
	)