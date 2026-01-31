import csv
import math
import numpy as np
import pandas as pd
import cvxpy as cp      # highly unfortunate abbreviation
import matplotlib
import matplotlib.pyplot as plt


SEASON = 20
# 1: ranking, 2: percentages, 3: fuck me
METHOD = 1 if 1 <= SEASON <= 2 else 2 if 3 <= SEASON <= 27 else 3


# read processed data
df1 = pd.read_csv('data/season_1_2.csv', header=0)
df2 = pd.read_csv('data/season_3_27.csv', header=0)
df3 = pd.read_csv('data/season_28_34.csv', header=0)
df = pd.concat([df1, df2, df3], ignore_index=True)
column_headers = df.columns.tolist()

# copy df for sorting
season_data = df[df['season'] == SEASON].copy(deep=True)  # copying season 3
season_data.sort_values(by='placement', inplace=True)
print(f"Season {SEASON} Data:\n", season_data)
print()

# number of weeks season ran for
temp_col_names = [f"week{i}_all_judge_score" for i in range(1, 12)]
num_weeks = 11 - season_data[temp_col_names].isna().all().sum()
num_ppl = len(season_data)     # no header
print(f"Week Count: {num_weeks}")
print(f"Contestants: {num_ppl}")
print()


# celebrity_name
# ballroom_partner
# celebrity_industry
# celebrity_homestate
# celebrity_homecountry/region
# celebrity_age_during_season
# season
# results
# placement
# week[i]_judge[j]_score
# week[i]_avg_judge_score
# week[i]_all_judge_score
# week[i]_rank_judge_score
# week[i]_percent_judge_score


def find_cont_num(cur_week: int):  # RETURNS: current contestants, eliminations (both placements idx)
    '''find current contestants & eliminations for that week'''
    cur_cont_raw = season_data[season_data[f"week{cur_week}_all_judge_score"].notna()]
    cur_cont = sorted(list(cur_cont_raw['placement']))
    elims = []      # 1-base

    if cur_week == 1:
        elims = sorted(list(season_data[season_data[f"week{cur_week + 1}_all_judge_score"].isna()]['placement']))
    # elif cur_week == week_cnt:
    #     elims = sorted(list(cur_cont_raw[cur_cont_raw['placement'] != 1]['placement']))
    else:
        all_gone = season_data[season_data[f"week{cur_week + 1}_all_judge_score"].isna()]
        elims = sorted(list(all_gone[all_gone[f"week{cur_week}_all_judge_score"].notna()]['placement']))
    return cur_cont, elims


def compute_constraints_perc(cur_cont: list, elims: list, j_perc: list):
    '''compute maximum vote percentages for eliminated, apply to find constraints for remaining'''
    # calculate range for all eliminations
    j_perc_elims = [j_perc[i - 1] for i in elims]  # 0-base
    elim_sort = sorted(list(zip(j_perc_elims, elims)), reverse=True)  # (j, idx = k', 1-base)
    
    # compute ranges for eliminations with highest j_perc values
    elim_range_temp = []
    for idx, el in enumerate(elim_sort):
        j_perc_ex = sum([item[0] for item in elim_sort[: idx]])
        max_pk = (1 + sum(j_perc) - j_perc_ex - (len(cur_cont) - idx) * el[0]) / (len(cur_cont) - idx)
        elim_range_temp.append((el[1], max_pk))

    elim_ranges = [item[1] for item in sorted(elim_range_temp)]  # [max_pk-l, ..., max_pk]

    # calculate min/max floor for all non-eliminations
    vote_constraints = []  # [(min_floor_1, max_floor_1), ..., (min_floor_n, max_floor_n)]
    for i in range(0, elims[0] - 1):
        min_floor_cand = [0] + [0 + j_perc[elims[j] - 1] - j_perc[i] for j in range(len(elims))]
        min_floor = max(min_floor_cand)

        max_floor_cand = [elim_ranges[j] + j_perc[elims[j] - 1] - j_perc[i] for j in range(len(elims))]
        max_floor = max(max_floor_cand)
        vote_constraints.append((min_floor, max_floor))

    return vote_constraints, elim_ranges


def compute_constraints_rank(cur_cont: list, elims: list, j_rank: list):
    '''compute highest vote ranks for eliminated, apply to find (inclusive) rank constraints for remaining'''
    # assumed max one elimination (holds for seasons 1,2)
    assert len(elims) == 1
    elim_max_rank = len(cur_cont)    # inclusive
    elim_min_rank_raw = (len(cur_cont) + 1) / 2  - j_rank[elims[0] - 1] + 1 / len(cur_cont) * sum(j_rank[:elims[0]])
    elim_min_rank = int(math.floor(elim_min_rank_raw + 1))
    elim_ranges = [(elim_max_rank, elim_min_rank)]

    # calculate min/max floor for all non-eliminations
    rank_constraints = []
    for i in range(0, elims[0] - 1):
        max_rank_cand = [len(cur_cont), elim_max_rank + j_rank[elims[0] - 1] - j_rank[i] - 1]   # inclusive
        max_rank = min(max_rank_cand)
        min_rank_cand = [len(cur_cont), elim_min_rank + j_rank[elims[0] - 1] - j_rank[i] - 1]     # inclusive
        min_rank = min(min_rank_cand)
        rank_constraints.append((max_rank, min_rank))
    
    return rank_constraints, elim_ranges


def compute_optimum_final_perc(contestants: list, j_perc: list):
    '''Runs quadratic program to find optimum for vote percentages (min square sum)'''
    # variable
    vote_percs = cp.Variable(len(contestants))  # 0-based
    objective = cp.Minimize(cp.sum_squares(vote_percs))
    constraints = [
        0 <= vote_percs, 
        vote_percs <= 1, 
        cp.sum(vote_percs) == 1
    ]
    for i in range(0, len(contestants) - 1):
        for j in range(i + 1, len(contestants)):
            constraints.append(vote_percs[i] - vote_percs[j] >= j_perc[j] - j_perc[i])
    prob = cp.Problem(objective, constraints)

    obj_value = prob.solve()
    var_values = vote_percs.value

    for i in range(0, len(contestants)):
        print(f"Place {i + 1} vote %: {var_values[i] * 100:.2f}")
    print(f"Objective Value: {obj_value:.6f}")


def compute_optimum_final_rank(contestants: list, j_rank: list):
    '''Runs integer program to find ONE optimum for vote ranks'''
    n = len(contestants)
    # variable --> var[i][k] = 0,1 --> v_i = k
    vote_rank_bin = cp.Variable((n, n), boolean=True)
    # vote_ranks = cp.Variable(len(contestants), integer=True)  # 0-based

    # find ANY optimum that satisfies all constraints
    objective = cp.Minimize(0)
    constraints = [
        # {v_1, ..., v_n} = {1, ..., n}
        cp.sum(vote_rank_bin, axis=0) == 1,
        cp.sum(vote_rank_bin, axis=1) == 1,
    ]

    for i in range(0, n - 1):
        for j in range(i + 1, n):
            v_i = sum([(k + 1) * vote_rank_bin[i][k] for k in range(0, n)])
            v_j = sum([(k + 1) * vote_rank_bin[j][k] for k in range(0, n)])

            constraints.append(v_i <= v_j + j_rank[j] - j_rank[i] - 1)      # inclusive
    prob = cp.Problem(objective, constraints)

    obj_value = prob.solve()
    var_values = vote_rank_bin.value


    for i in range(0, len(contestants)):
        vote_rank = sum([(k + 1) * var_values[i][k] for k in range(0, n)])
        print(f"Place {i + 1} vote rank: {vote_rank}")


# constraints container
vote_ranks = []         # Wk1: [v_1, ..., v_n], Wk2: [v_1, ..., v_n], ...
vote_percentages = []   # Wk1: [p_1, ..., p_n], Wk2: [p_1, ..., p_n], ...

# iterate through each week, 1-base
for cur_week in range(1, num_weeks + 1): 
    # find current contestants & eliminations
    cur_cont, elims = find_cont_num(cur_week)

    # if no eliminations, no conclusions regarding vote percentages can be made
    if len(elims) == 0:
        print(f"############## WEEK {cur_week} ##############")
        print(f"Eliminations: None")
        print()
        continue
    
    if METHOD == 1:
        # retrieve judge rankings, 0-base
        j_rank = list(season_data[f"week{cur_week}_rank_judge_score"].iloc[0: elims[-1]])
    elif METHOD == 2:
        # retrieve judge percentages, 0-base
        j_perc = list(season_data[f"week{cur_week}_percent_judge_score"].iloc[0: elims[-1]])
    else:
        pass

    # if final week --> RUN QUADRATRIC/INTEGER PROGRAM
    if cur_week == num_weeks:
        assert len(cur_cont) == len(elims)
        print(f"############## WEEK {cur_week} ##############")
        print(f"Final Week: Full Rankings")
        if METHOD == 1:
            vote_ranks = compute_optimum_final_rank(elims, j_rank)          # prints in function
        elif METHOD == 2:
            vote_percentages = compute_optimum_final_perc(elims, j_perc)    # prints in function
        else:
            pass
        break

    # else (intermediate week) --> compute range for eliminated, apply constraints to remaining contestants
    if METHOD == 1:
        rank_constraints, elim_ranges = compute_constraints_rank(cur_cont, elims, j_rank)
        vote_ranks.append(rank_constraints)
    elif METHOD == 2:
        vote_constraints, elim_ranges = compute_constraints_perc(cur_cont, elims, j_perc)
        vote_percentages.append(vote_constraints)
    else:
        pass

    print(f"############## WEEK {cur_week} ##############")
    print(f"Eliminations: {elims}")

    if METHOD == 1:
        for idx, item in enumerate(rank_constraints):
            print(f"Place {idx + 1} vote rank min: <{item[0]}, {item[1]}>")
        for idx, el in enumerate(elims):
            print(f"Place {el} vote rank range: [{elim_ranges[idx][0]}, {elim_ranges[idx][1]}]")
    elif METHOD == 2:
        for idx, item in enumerate(vote_constraints):
            print(f"Place {idx + 1} vote % strict min: <{f"{item[0] * 100:.2f}" if item is not None else "N/A"}, {f"{item[1] * 100:.2f}" if item is not None else "N/A"}>")
        for idx, el in enumerate(elims):
            print(f"Place {el} vote % range: [0, {elim_ranges[idx] * 100:.2f})")
    else:
        pass
    print()
