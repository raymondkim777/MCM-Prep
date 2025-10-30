import numpy as np
# Constants
P = 7  # $ per kg for food

# -----------------------------
# 1. Food Cost
# -----------------------------
def cost_food(M, caloric, H):
    """
    Food cost per month.
    Parameters:
        M : float
            Dragon mass (kg)
        caloric : callable
            Function F(M) returning caloric requirement (kg of food equivalent)
        H : float
            Baseline harvesting level (same unit as F)
    """
    return (caloric(M) - H) * P


# -----------------------------
# 2. People Cost
# -----------------------------
def cost_people(M):
    """
    Monthly cost for zookeepers, vets, and healthcare.
    Formula: 1/12 * [200000*(M/40)^0.4 + 125000*(M/10)^0.25] * 1.08
    """
    return (1 / 12) * (200000 * (M / 40) ** 0.4 + 125000 * (M / 10) ** 0.25) * 1.08


# -----------------------------
# 3. Logistics Cost
# -----------------------------
def cost_logistics(M):
    """
    Monthly logistics and maintenance cost.
    Environmental facility: (1/12)*20000*(M/10)^0.5
    Infrastructure maintenance: 5000*(M/10)^1
    """
    env_facility = (1 / 12) * 20000 * (M / 10) ** 0.5
    maintenance = 5000 * (M / 10)
    return env_facility + maintenance


# -----------------------------
# 4. Space Cost
# -----------------------------
def cost_space(M):
    """
    Space cost (million $):
    C = (M/10)*247*5
    """
    return (M / 10) * 247 * 5  # in million $


def caloric(M):
    """Example caloric model F(M): proportional to M^0.75."""
    return 50 * (M ** 0.75)


def cost_food_vec(M, caloric, H):

    M = np.asarray(M)
    F_M = np.asarray(caloric1(M))
    return (F_M - H) * P

def cost_people_vec(M):
    """
    Vectorized monthly people cost.
    """
    M = np.asarray(M)
    return (1 / 12) * (200000 * (M / 40) ** 0.4 + 125000 * (M / 10) ** 0.25) * 1.08

def cost_logistics_vec(M):
    M = np.asarray(M)
    env_facility = (1 / 12) * 20000 * (M / 10) ** 0.5
    maintenance = 5000 * (M / 10)
    return env_facility + maintenance

def cost_space_vec(M):
    M = np.asarray(M)
    return (M / 10) * 4000  # in $/month

def caloric1(M):
    return 50 * np.power(M, 0.75)

# Baseline harvesting level
H = 100  # kg of food dragon eats each month?

# if __name__ == "__main__":
#     M = 100  # example dragon mass (kg)
#     print("Food cost ($):", cost_food(M, caloric, H))
#     print("People cost ($/month):", cost_people(M))
#     print("Logistics cost ($/month):", cost_logistics(M))
#     print("Space cost (million $):", cost_space(M))


if __name__ == "__main__":
    M = np.array([10, 20, 50, 100, 200])  # example masses
    print("Food cost ($):", cost_food_vec(M, caloric, H))
    print("People cost ($/month):", cost_people_vec(M))
    print("Logistics cost ($/month):", cost_logistics_vec(M))
    print("Space cost ($/month):", cost_space_vec(M))