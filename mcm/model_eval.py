import csv
import numpy as np
import pandas as pd
import cvxpy as cp      # highly unfortunate abbreviation
import matplotlib
import matplotlib.pyplot as plt


DO_PRINT_WEEK = False
DO_PRINT_SEASON = True


# processed dwts data
df = pd.read_csv('data/season_3_27.csv', header=0)
column_headers = df.columns.tolist()


# fan estimate data
df2 = pd.read_csv('data/dwts_fan_estimates.csv', header=0)
column_headers2 = df2.columns.tolist()
all_seasons = sorted(list(set(df2['season'])))
# ! FIX LATER
all_seasons = all_seasons[2:]


def find_cont_num(season_data, cur_week: int):  # RETURNS: current contestants, eliminations (both placements idx)
    '''find current contestants & eliminations for that week'''
    cur_cont_raw = season_data[season_data[f"week{cur_week}_all_judge_score"].notna()]
    cur_cont = sorted(list(cur_cont_raw['placement']))
    elims = []      # (idx, j_perc[idx]), 1-base

    if cur_week == 1:
        elims = sorted(list(season_data[season_data[f"week{cur_week + 1}_all_judge_score"].isna()]['placement']))
    # elif cur_week == week_cnt:
    #     elims = sorted(list(cur_cont_raw[cur_cont_raw['placement'] != 1]['placement']))
    else:
        all_gone = season_data[season_data[f"week{cur_week + 1}_all_judge_score"].isna()]
        elims = sorted(list(all_gone[all_gone[f"week{cur_week}_all_judge_score"].notna()]['placement']))
    return cur_cont, elims


# fan estimate data, 0-base idx
vote_percentages = []  # [(season 1) [week1, week2, ...], (season2) [week1, week2, ...], ...

for season in all_seasons:
    if DO_PRINT_WEEK:
        print(f"############## SEASON {season} ##############")

    # extract vote data for seeason
    season_vote_percentages = []
    cur_season_vote_data = df2[df2['season'] == season]
    num_weeks = sorted(list(set(cur_season_vote_data['week'])))[-1]
    num_ppl = len(cur_season_vote_data[cur_season_vote_data['week'] == 1])

    for cur_week in range(1, num_weeks + 1):
        cur_week_data = cur_season_vote_data[cur_season_vote_data['week'] == cur_week].copy(deep=True)
        cur_week_data.sort_values(by='placement', inplace=True)
        
        vote_data = list(cur_week_data['fan_mean'])
        # pad 0s (since eliminattions are removed from vote data)
        vote_data += [0 for _ in range(num_ppl - len(vote_data))]
        season_vote_percentages.append(vote_data)
    vote_percentages.append(season_vote_percentages)

    # extract raw data for season
    season_data = df[df['season'] == season].copy(deep=True)  # copying season 3
    season_data.sort_values(by='placement', inplace=True)

    #####################################################

    # COMPUTE CONSTRAINT MATCH RATE
    total_constraints = 0
    matched_constraints = 0

    # iterate through each week, 1-base, assume eliminated each week
    for cur_week in range(1, num_weeks + 1): 
        # init
        week_total_constraints = 0
        week_matched_constraints = 0

        # filter for weekly vote data
        week_vote_percentages = season_vote_percentages[cur_week - 1]

        # find current contestants & eliminations
        cur_cont, elims = find_cont_num(season_data, cur_week)

        # if no eliminations, no conclusions regarding vote percentages can be made
        if len(elims) == 0:
            if DO_PRINT_WEEK:
                print(f"############## WEEK {cur_week} ##############")
                print(f"Eliminations: None")
                print()
            continue

        # compute judge percentages, 0-base
        j_perc = list(season_data[f"week{cur_week}_percent_judge_score"].iloc[0: elims[-1]])

        # if final week --> compute all quadratic/linear program constraints
        if cur_week == num_weeks:
            assert len(cur_cont) == len(elims)
            for i in range(0, len(cur_cont) - 1):
                for j in range(i + 1, len(cur_cont)):
                    total_constraints += 1
                    week_total_constraints += 1
                    if week_vote_percentages[i] - week_vote_percentages[j] >= j_perc[j] - j_perc[i]:
                        matched_constraints += 1
                        week_matched_constraints += 1
            if DO_PRINT_WEEK:
                print(f"############## FINAL WEEK ##############")
                print(f"Eliminations: {elims}")
                print(f"Total: {week_total_constraints}")
                print(f"Matched: {week_matched_constraints}")
                print(f"Match Rate %: {week_matched_constraints / week_total_constraints * 100:.2f}")
                print()
            break

        # else (intermediate week) --> compute constraints applied to remaining by eliminated
        for i in range(len(elims)):
            el = elims[i]  # 1-base
            for j in range(len(cur_cont) - len(elims)):
                total_constraints += 1
                week_total_constraints += 1
                if week_vote_percentages[j] - week_vote_percentages[el - 1] > j_perc[el - 1] - j_perc[j]:
                    matched_constraints += 1
                    week_matched_constraints += 1

        if DO_PRINT_WEEK:
            print(f"############## WEEK {cur_week} ##############")
            print(f"Eliminations: {elims}")
            print(f"Total: {week_total_constraints}")
            print(f"Matched: {week_matched_constraints}")
            print(f"Match Rate %: {week_matched_constraints / week_total_constraints * 100:.2f}")
            print()
    if DO_PRINT_SEASON:
        print(f"############## RESULTS FOR SEASON {season} ##############")
        print(f"Total: {total_constraints}")
        print(f"Matched: {matched_constraints}")
        print(f"Match Rate %: {matched_constraints / total_constraints * 100:.2f}")


