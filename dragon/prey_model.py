import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


# Parameters
r = 0.317        # growth rate for a year
r_month = np.float_power(r, 1/12)  # monthly growth rate
K = 20000        # carrying capacity
H = 1500        # harvesting amt
p0 = 13000       # initial population

# Time range (months)
t_span = (0, 50)  # simulate 50 months
t_eval = np.linspace(*t_span, 500)


# Differential equation dx/dt
def caribou_model(t, p):
    return r * p * (1 - p / K) - H


def get_pop_fixed_pts(harvest_amt):
    # check whether H is too high
    if H > r * K / 4:
        raise ValueError("Harvesting rate too high, definite extinction")
    p_min = (K - np.sqrt(K ** 2 - 4 * K * harvest_amt / r)) / 2
    p_max = (K + np.sqrt(K ** 2 - 4 * K * harvest_amt / r)) / 2
    return p_min, p_max


def get_max_harvest():
    return caribou_model(0, K / 2) + H


def solve(model, x0, t_span, t_eval):
    # Solve the model
    sol = solve_ivp(model, t_span, [x0], t_eval=t_eval)

    # Plot the results
    # plt.figure(figsize=(8, 5))
    # plt.plot(sol.t, sol.y[0], label=f'h = {h}')
    # plt.axhline(K, color='blue', linestyle='--', label='Carrying Capacity')
    # plt.xlabel('Time (months)')
    # plt.ylabel('Caribou Population')
    # plt.title('Caribou Population with Harvesting')
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    return sol


# TODO: Add code to find next month's pop, and how much pop to refill
# TODO: to ensure pop doesn't go extinct


def prey_model(pop_cur, harvest_amt):
    assert harvest_amt <= pop_cur
    global H
    H = harvest_amt
    caribou_sol = solve_ivp(caribou_model, t_span, [pop_cur], t_eval=t_eval)
    idx = min(range(len(caribou_sol.t)), key=lambda i: abs(caribou_sol.t[i]-(1/12)))
    new_pop = caribou_sol.y[0][idx]
    min_pop, max_pop = get_pop_fixed_pts(harvest_amt)
    return {
        'p_next': new_pop,
        'p_min': min_pop,
        'p_max': max_pop
    }


if __name__ == '__main__':
    caribou_sol = solve(caribou_model, p0, t_span, t_eval)
    idx = min(range(len(caribou_sol.t)), key=lambda i: abs(caribou_sol.t[i]-(1/12)))
    new_pop = caribou_sol.y[0][idx]
    min_pop, max_pop = get_pop_fixed_pts(H)
    max_harvest = caribou_model(5, K / 2) + H
    print(new_pop)
    print(min_pop)
    print(max_pop)
    print(max_harvest)