import numpy as np
# Constants
P = 7  # $ per kg for food

# -----------------------------
# 1. Food Cost
# -----------------------------

def caloric(M):
    """Example caloric model F(M): proportional to M^0.75."""
    return 50 * (M ** 0.75)


# def cost_food_vec(M, caloric, H):

#     M = np.asarray(M)
#     F_M = np.asarray(caloric1(M))
#     return (F_M - H) * P

def cost_food_vec(food_vec):
    return P * np.asarray(food_vec)

def cost_people_vec(M):
    """
    Vectorized monthly people cost.
    """
    M = np.asarray(M)
    return (1 / 12) * (100000 * (M / 40) ** 0.3 + 120000 * (M / 10) ** 0.15) * 1.08

def cost_logistics_vec_phase1(M):
    M = np.asarray(M)
    
    # Constants
    c_move = 50000      # USD, one-time infrastructure move
    I_move = 0.004          # 1 if relocation this month, else 0
    c_deliv = 0.3       # USD/kg, feed delivery cost
    c_sup = 250         # USD/staff·month, training & medical supplies
    b_keeper = 0.3
    b_vet = 0.15
    
    F_M = np.asarray(caloric1(M))
    
    n_staff = 5 * (M / 10) ** b_keeper + (M / 10) ** b_vet
    
    # Cost components
    move_cost = c_move * I_move
    delivery_cost = c_deliv * F_M
    supply_cost = c_sup * n_staff
    
    # Total monthly logistics cost
    return move_cost + delivery_cost + supply_cost

def cost_logistics_open_vec_phase2(M):
    M = np.asarray(M)

    c_pat = 600         # USD per km of ground patrol per month
    L_ring = 390        # km, perimeter length of the protected area
    c_drone = 300       # USD per flight hour
    h_drone = 25        # hours of drone/helicopter flight per month
    c_handle = 1        # USD per kg of caribou
    
    F_M = np.asarray(caloric1(M))
    
    patrol_cost = c_pat * L_ring
    drone_cost = c_drone * h_drone
    handling_cost = c_handle * np.minimum(F_M, H)
    
    return patrol_cost + drone_cost + handling_cost
    

def cost_space_vec(M):
    M = np.asarray(M)
    land = (M / 10) * 4000
    env_facility = (1 / 12) * 8000 * (M / 10) ** 0.3
    maintenance = 1200 * (M / 10) ** 0.8
    return land + env_facility + maintenance

def caloric1(M):
    return 50 * np.power(M, 0.75)

# Baseline harvesting level
H = 100

# if __name__ == "__main__":
#     M = 100  # example dragon mass (kg)
#     print("Food cost ($):", cost_food(M, caloric, H))
#     print("People cost ($/month):", cost_people(M))
#     print("Logistics cost ($/month):", cost_logistics(M))
#     print("Space cost ($/month):", cost_space(M))


if __name__ == "__main__":
    M = np.array([10, 20, 50, 100, 200])  # example dragon masses (kg)

    print("Food cost ($/month):", cost_food_vec(M, caloric1, H))
    print("People cost ($/month):", cost_people_vec(M))
    print("Logistics cost – Phase 1 (Zoo) ($/month):", cost_logistics_vec_phase1(M))
    print("Logistics cost – Phase 2 (Open) ($/month):", cost_logistics_open_vec_phase2(M))
    print("Space cost ($/month):", cost_space_vec(M))