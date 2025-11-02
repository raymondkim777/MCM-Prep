import numpy as np
import argparse
from mass_model import mass_model
from prey_model import prey_model, get_max_harvest
from cost_model import cost_food_vec, cost_people_vec, cost_logistics_vec, cost_space_vec
import tabulate


DRAGON_CNT = 1
GROWTH_RATE_1 = np.power(3, 1/12)
GROWTH_RATE_2 = np.power(208013628 / 10, 1/(310 * 12))
# GROWTH_RATE_2 = np.power(3, 1/12)
CAL_COEFF = 0.2209
CAL_PER_KG = 5000
MAX_KG_P1 = 8000
MAX_KG_P2 = 200000000000
KG_PER_CARIBOU = 45


def _parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--n', type=int, default=50, help='number of trials to run model')
	parser.add_argument('--t', type=int, default=120, help='number of months')
	parser.add_argument('--tm', type=int, default=30, help='number of days in a month')
	parser.add_argument('--fire', type=int, default=4, help='average days in a month dragon breathes fire')
	parser.add_argument('--f', type=float, default=1, help='average proportion of food to feed dragon (0~1)')
	parser.add_argument('--m0', type=float, default=10, help='initial dragon mass')
	parser.add_argument('--phase2', action="store_true")
	parser.add_argument('--p0', type=float, default=13000, help='initial caribou population')
	parser.add_argument('--k', type=float, default=20000, help='caribou population carrying capacity')
	parser.add_argument('--pr', type=float, default=0.317, help='annual caribou population growth rate')
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
		args
		# n = 50,     # trial number
		# t = 120,    # number of months to run model
		# d = 30,     # days in a month
		# lam = 4,    # average number of fire days per month
		# f = 0.5,	# average proportion of food to feed dragon (0~1)
		# m_0 = 10,   # initial dragon mass
		# phase2 = False,
	):
	
	# unpack args
	n, t, d, lam, f, m_0 = args.n, args.t, args.tm, args.fire, args.f, args.m0
	phase2 = args.phase2
	p_init, pK, pr = args.p0, args.k, args.pr


	all_p1_mass_list = []
	all_p1_food_list = []
	all_p1_fire_list = []
	all_p1_food_cost = []
	all_p1_empl_cost = []
	all_p1_logi_cost = []
	all_p1_spac_cost = []

	all_p2_mass_list = []
	all_p2_food_list = []
	all_p2_fire_list = []
	all_p2_cari_pop_list = []
	all_p2_cari_add_list = []
	all_p2_food_cost = []
	all_p2_empl_cost = []
	all_p2_logi_cost = []
	all_p2_spac_cost = []
	
	# run trials
	for trial in range(n):
		p1_mass_list = []
		p1_food_list = []
		p1_fire_list = []

		p2_mass_list = []
		p2_food_list = []
		p2_fire_list = []
		p2_cari_pop_list = []
		p2_cari_add_list = []

		# initalize mass
		cur_mass = np.float64(m_0)

		# initialize AREA prey model (for phase 2)
		pop_caribou = p_init
		
		# START WITH PHASE 1
		phase_2_flag = False

		# iterate through each month
		for month in range(t): 

			# DRAGON MASS SECTION
			food_prop_p1 = f
			if cur_mass >= MAX_KG_P1:
				if phase2:
					# switch to phase 2
					phase_2_flag = True
				else:
					# cap dragon mass
					food_prop_p1 = 0 
			
			if not phase_2_flag:
				# PHASE 1
				cur_food, cur_fire = calculate_monthly_food(cur_mass, food_prop=food_prop_p1, d=d, lam=lam)

				# append mass/food to trial list phase1
				p1_mass_list.append(cur_mass.item())
				p1_food_list.append(cur_food.item())
				p1_fire_list.append(cur_fire)

				# update mass based on food_prop
				growth_rate = GROWTH_RATE_1 if month < 48 else GROWTH_RATE_2
				mass_growth = 1 + food_prop_p1 * (growth_rate - 1)
				cur_mass *= mass_growth
			else:
				# PHASE 2
				food_prop_p2 = f
				cur_food, cur_fire = calculate_monthly_food(cur_mass, food_prop=food_prop_p2, d=d, lam=lam)

				# compare food req (kg) with available max caribou harvest population
				# NOTE: This is for all 3 dragons
				p_harvest = int(cur_food * DRAGON_CNT / KG_PER_CARIBOU)  # round down

				# dragon needs too much food
				if p_harvest > get_max_harvest():
					# log
					with open('log.txt', 'a', encoding='utf-8') as f:
						f.write(f"Trial {trial}: Dragon got too big, required food exceeded maximum harvest - Limiting dragon food intake\n")
					
					raise ValueError("dragon got too big")
				
				# append mass/food to trial list phase2
				p2_mass_list.append(cur_mass)
				p2_food_list.append(cur_food)
				p2_fire_list.append(cur_fire)

				harvest_results = prey_model(pop_caribou, p_harvest)
				p2_cari_pop_list.append(harvest_results['p_next'])

				# update caribou pop
				pop_caribou = harvest_results['p_next']

				# overharvesting
				if harvest_results['p_next'] < harvest_results['p_min']:
					p2_cari_add_list.append((trial, harvest_results['p_min'] - harvest_results['p_next']))
					# re-add caribou
					pop_caribou = harvest_results['p_min']
				
				# update mass based on food_prop
				if cur_mass < MAX_KG_P2:
					growth_rate = GROWTH_RATE_1 if month < 48 else GROWTH_RATE_2
					mass_growth = 1 + food_prop_p2 * (growth_rate - 1)
					cur_mass *= mass_growth
		
		# appending trial result
		if phase2:
			# final padding
			p2_mass_list.append(cur_mass)
			p2_food_list.append(0)
			p2_fire_list.append(0)
			p2_cari_pop_list.append(0)
			p2_cari_add_list.append(0)

			# append trials
			all_p1_mass_list.append(p1_mass_list)
			all_p1_food_list.append(p1_food_list)
			all_p1_fire_list.append(p1_fire_list)

			all_p2_mass_list.append(p2_mass_list)
			all_p2_food_list.append(p2_food_list)
			all_p2_fire_list.append(p2_fire_list)
			all_p2_cari_pop_list.append(p2_cari_pop_list)
			all_p2_cari_add_list.append(p2_cari_add_list)
		
		else:
			# final padding
			p1_mass_list.append(cur_mass)
			p1_food_list.append(0)
			p1_fire_list.append(0)

			# append trials
			all_p1_mass_list.append(p1_mass_list)
			all_p1_food_list.append(p1_food_list)
			all_p1_fire_list.append(p1_fire_list)
	
		# compute costs
		# all_p1_food_cost = []
		# all_p1_empl_cost = []
		# all_p1_logi_cost = []
		# all_p1_spac_cost = []

		all_p1_food_cost.append(list(cost_food_vec(p1_food_list)))
		all_p1_empl_cost.append(list(cost_people_vec(p1_mass_list)))
		all_p1_logi_cost.append(list(cost_logistics_vec(p1_mass_list)))
		all_p1_spac_cost.append(list(cost_space_vec(p1_mass_list)))

		p2_extra_food_list = np.asarray(p2_cari_add_list) * KG_PER_CARIBOU
		all_p2_food_cost.append(list(cost_food_vec(p2_extra_food_list)))
		all_p2_empl_cost.append(list(cost_people_vec(p2_mass_list)))
		all_p2_logi_cost.append(list(cost_logistics_vec(p2_mass_list)))
		all_p2_spac_cost.append(list(cost_space_vec(p2_mass_list)))
	
	# print results from all trials
	trial_cnt = len(all_p1_mass_list)
	trial_data_1 = []
	max_month_cnt = 0
	for trial in range(trial_cnt):
		max_month_cnt = max(max_month_cnt, len(all_p1_mass_list[trial]))
	
	trial_costs = []

	for trial in range(trial_cnt):
		p1_mass_list = all_p1_mass_list[trial]
		p1_food_list = all_p1_food_list[trial]
		p1_fire_list = all_p1_fire_list[trial]

		total_cost = sum(all_p1_food_cost[trial]) 
		+ sum(all_p1_empl_cost[trial])
		+ sum(all_p1_logi_cost[trial])
		+ sum(all_p1_spac_cost[trial])
		trial_costs.append(total_cost)

		trial_data_1.append(([trial + 1, 'Mass'] + p1_mass_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [total_cost])
		trial_data_1.append(([trial + 1, 'Food'] + p1_food_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [0])
		trial_data_1.append(([trial + 1, 'Fire'] + p1_fire_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [0])

	with open('results.txt', 'w', encoding='utf-8') as f:
		f.write(f"PHASE 1 - ({max_month_cnt - 1} months)\n")
		headers = ['Trial', 'Type'] + [i for i in range(max_month_cnt)] + ['Total Cost']
		f.write(tabulate.tabulate(trial_data_1, headers=headers, floatfmt=".2f"))

	if phase2:
		trial_cnt = len(all_p2_mass_list)
		trial_data_2 = []
		max_month_cnt = 0
		for trial in range(trial_cnt):
			max_month_cnt = max(max_month_cnt, len(all_p2_mass_list[trial]))
			p2_mass_list = all_p2_mass_list[trial]
			p2_food_list = all_p2_food_list[trial]
			p2_fire_list = all_p2_fire_list[trial]
			p2_cari_pop_list = all_p2_cari_pop_list[trial]
			p2_cari_add_list = all_p2_cari_add_list[trial]

			total_cost = sum(all_p2_food_cost[trial]) 
			+ sum(all_p2_empl_cost[trial])
			+ sum(all_p2_logi_cost[trial])
			+ sum(all_p2_spac_cost[trial])

			final_cost = trial_costs[trial] + total_cost

			trial_data_2.append(([trial + 1, 'Mass'] + p2_mass_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [total_cost, final_cost])
			trial_data_2.append(([trial + 1, 'Food'] + p2_food_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [0, 0])
			trial_data_2.append(([trial + 1, 'Fire'] + p2_fire_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [0, 0])
			trial_data_2.append(([trial + 1, 'CPop'] + p2_cari_pop_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [0, 0])
			trial_data_2.append(([trial + 1, 'CAdd'] + p2_cari_add_list + [0] * max_month_cnt)[:max_month_cnt + 3] + [0, 0])

		with open('results.txt', 'a', encoding='utf-8') as f:
			f.write(f"\n\nPHASE 2 - ({max_month_cnt - 1} months)\n")
			headers = ['Trial', 'Type'] + [i for i in range(t + 1)] + ['Total Cost', 'Final Cost']
			f.write(tabulate.tabulate(trial_data_2, headers=headers, floatfmt=".2f"))


	


if __name__ == "__main__":
	np.random.seed(42)

	args = _parse_args()
	mass_model(args)
	# mass_model(
	# 	n = args.n,         # number of trials
	# 	t = args.t,         # number of months to run model
	# 	d = args.tm,        # days in a month
	# 	lam = args.fire,    # average number of fire days per month
	# 	r = args.r,         # average yearly mass growth rate
	# 	f = args.f,
	# 	m_0 = args.m0,       # initial dragon mass
	# 	phase2 = args.phase2,
	# )
