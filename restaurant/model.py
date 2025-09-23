import argparse
import pulp
import math
from typing import Tuple, Dict


################## INITIAL MODEL ##################


# Base model to compute baseline number of reviewers and cost (confirmation of calculations)
def reviewers_for_days(total_restaurants: int, days: int, cost_per_review: float = 200.0):
	"""

	Variables:
		r: integer number of reviewers (>= 0)

	Constraints:
		r * days >= total_restaurants

	Objective:
		Minimize total cost = r * days * cost_per_review
	"""
	# This function uses the linear program to minimize cost
	# while ensuring enough reviewer-days to cover all restaurants.
	# Minimization LP
	prob = pulp.LpProblem(f"Reviewers_{days}d", pulp.LpMinimize)

	# Integer variable: number of reviewers
	r = pulp.LpVariable("reviewers", lowBound=0, cat="Integer")

	# Objective: minimize total money paid = r * days * cost_per_review
	prob += r * days * cost_per_review

	# Constraint: each reviewer does 1 restaurant/day, so r * days >= total_restaurants
	prob += r * days >= total_restaurants

	# Solve
	prob.solve()

	status = pulp.LpStatus[prob.status]
	reviewers_val = int(pulp.value(r)) if pulp.value(r) is not None else None
	total_cost = reviewers_val * days * cost_per_review if reviewers_val is not None else None

	return {
		"status": status,
		"reviewers": reviewers_val,
		"total_cost": total_cost,
		"days": days,
		"total_restaurants": total_restaurants,
	}


def compute_reviewers_and_cost(nR: int, t: int, w: int, r: int, cr: float, cf: float) -> Dict[str, float]:
	"""Compute number of reviewers needed and total cost using the equations provided.

	Equations
		nr = CEIL(nR / (r * t))
		c  = nr * nR * r * t * (cr + cf)  <
	"""
	if nR < 0 or t <= 0 or r <= 0:
		raise ValueError("nR must be >= 0, and t and r must be > 0")

	reviewers_needed = math.ceil(nR * w/ (r * t)) if (r * t) > 0 else None

	#Formula literally: c = nr * r * t * (cr + cf)
	cost_formula = None
	if reviewers_needed is not None:
		cost_formula = reviewers_needed * r * t * (cr + cf)

	# Conventional interpretation: total cost = total_reviews * (cr + cf)
	cost_per_review = nR * (cr + cf)

	# Alternative: if cost is per reviewer per day (salary+food per reviewer-day),
	# then total reviewer-days = reviewers_needed * t, and cost = reviewer-days * (cr+cf)
	cost_per_reviewer_day = reviewers_needed * t * (cr + cf) if reviewers_needed is not None else None

	return {
		"nR": nR,
		"t": t,
		"r": r,
		"cr": cr,
		"cf": cf,
		"nr": reviewers_needed,
		"cost_formula": cost_formula,
		"cost_per_review": cost_per_review,
		"cost_per_reviewer_day": cost_per_reviewer_day,
	}


def initial_model(
		nR: int, 
		t: int, 
		w: int,
		r: int, 
		cr: float, 
		cf: float,
	):

	res = compute_reviewers_and_cost(nR=nR, t=t, w=w, r=r, cr=cr, cf=cf)

	print("Results:")
	print(f"Number of restaurants = {nR}")
	print(f"Days = {t}")
	print(f"Reviews per day = {r}")
	print(f"Base salary = {cr}")
	print("nr (ceil):", res["nr"])  # reviewers needed
	print("Cost: $", res["cost_formula"]) 
	#print("cost_per_review (conventional):", res["cost_per_review"])  # cost per review * nR
	#print("cost_per_reviewer_day (v2):", res["cost_per_reviewer_day"])  # reviewer-days * (cr+cf)
	print()


################## REGIONAL MODEL ##################


def _parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--t', type=int, default=120, help='number of days')
	parser.add_argument('--w', type=int, default=1, help='reviews per restaurant')
	parser.add_argument('--r', type=int, default=1, help='reviews per reviewer per day')
	parser.add_argument('--cr', type=int, default=100, help='review salary')
	parser.add_argument('--cf', type=int, default=100, help='food allowance')
	parser.add_argument('--ct', type=int, default=50, help='travel allowance')

	parser.add_argument('--regional', action='store_true', help='runs regional model instead of basic model')
	return parser.parse_args()


def find_reviewer_cnt_per_region(
		region_res_cnt: list, 
		region_rev_cnt: list, 
		days: int, rate: int, weight: int,
	) -> list:

	reviewer_cnt = []

	for i in range(len(region_res_cnt)):
		rev_cnt = math.ceil(region_res_cnt[i] * weight / (rate * days))
		if rev_cnt <= region_rev_cnt[i]:
			reviewer_cnt.append(rev_cnt)
		else: 
			reviewer_cnt.append(-1)
	
	return reviewer_cnt


def compute_total_cost(
		region_res_cnt: list,
		reviewer_cnt: list, 
		days: int, rate: int, weight: int,
		cost_r: float, cost_f: float, cost_t: float
	) -> float:

	costs = []
	total_cost = 0
	for i in range(len(region_res_cnt)):
		days_required = math.ceil(region_res_cnt[i] * weight / (reviewer_cnt[i] * rate))
		review_cnt = reviewer_cnt[i] * rate * days_required
		add_cost = review_cnt * (cost_r + cost_f + cost_t)
		costs.append(add_cost)
		total_cost += add_cost
	print(costs)
	print(total_cost)
	return total_cost


def regional_model(
		region_res_cnt,		# array of restaurant cnts per region
		region_rev_cnt,		# array of max reviewers available per region
		t = 120,			# days
		w = 1,				# number of reviews per restaurant
		r = 1,				# number of reviews per reviewer per days
		c_r = 100.0,		# salary per review
		c_f = 100.0,		# food allowance per review
		c_t = 50,			# travel allowance per review
	):

	# number of reviewers (decision variable)
	reviewer_cnt = find_reviewer_cnt_per_region(
		region_res_cnt=region_res_cnt, 
		region_rev_cnt=region_rev_cnt, 
		days=t, rate=r, weight=w
	)

	total_cost = compute_total_cost(
		region_res_cnt=region_res_cnt,
		reviewer_cnt=reviewer_cnt, 
		days=t, rate=r, weight=w,
		cost_r=c_r, cost_f=c_f, cost_t=c_t
	)

	# OUTPUT
	with open("results.txt", "w") as f:
		# output parameters
		f.write("PARAMETERS:\n")
		f.write(f"Days = {t}\n")
		f.write(f"Reviews per restaurant = {w}\n")
		f.write(f"Review rate = {r}\n")
		f.write(f"Review salary = ${c_r}\n")
		f.write(f"Food allowance = ${c_f}\n")
		f.write(f"Travel allowance = ${c_t}\n")

		# output results
		f.write("\nRESULTS:\n")
		f.write(f"Total reviewers needed: {sum(reviewer_cnt)}\n")
		f.write(f"Reviewers needed per region:\n{reviewer_cnt}\n")

		f.write(f"\nTotal cost for {t} days:\n${total_cost}\n")


if __name__ == "__main__":

	# DATA INPUT
	total_restaurants = 2776
	region_res_cnt = [121, 315, 1768, 161, 86, 186, 139]		# array of restaurant cnts per region
	region_rev_cnt = [float("inf") for i in region_res_cnt]		# array of max reviewers available per region

	assert(sum(region_res_cnt) == total_restaurants)

	# parameters
	args = _parse_args()
	
	# run model
	if args.regional:
		regional_model(
			region_res_cnt=region_res_cnt, 
			region_rev_cnt=region_rev_cnt,
			t=args.t,			# days
			w=args.w,			# number of reviews per restaurant
			r=args.r,			# number of reviews per reviewer per days
			c_r=args.cr,		# salary per review
			c_f=args.cf,		# food allowance per review
			c_t=args.ct,		# travel allowance per review
		)
	else:
		initial_model(
			nR=total_restaurants,
			t=args.t,			# days
			w=args.w,			# number of reviews per restaurant
			r=args.r,			# number of reviews per reviewer per days
			cr=args.cr,		# salary per review
			cf=args.cf,		# food allowance per review
		)