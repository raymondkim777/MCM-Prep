import csv
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib
import matplotlib.pyplot as plt
import datetime
import time


final_data = []
df = pd.read_csv('data/alcarez_djokovic.csv', header=0)

# match_data = df[df['match_id'] == '2023-wimbledon-1701']
# momentum_deltas = np.array([])  # momentum values derived from flow model

'''
Features:
- Serve: (-1)^{data['server'] - 1}
- Victor: (-1)^{data['point_victor'] - 1} * (1 + |data['server'] - data['point_victor']|)
- Ace: int(data['p1_ace'] + data['p2_ace'] > 0) * (-1)^{data['server'] - 1}
- Volley: data['rally_count'] * (-1)^{data['point_victor'] - 1}
- Distance: data['p2_distance_run'] - data['p1_distance_run']
- Error: data['p1_unf_err'] * (data['point_victor'] - 1) + data['p2_unf_err'] * (2 - data['point_victor'])
'''

features = []
for idx, row in df.iterrows():
    cur_list = [
        np.power(-1, row['server'] - 1),                                                                    # serve
        # np.power(-1, row['point_victor'] - 1) * (1 + np.abs(row['server'] - row['point_victor'])),          # victor
        int(row['p1_ace'] + row['p2_ace'] > 0) * np.power(-1, row['server'] - 1),                           # ace
        row['rally_count'] * np.power(-1, row['point_victor'] - 1),                                         # volley
        row['p2_distance_run'] - row['p1_distance_run'],                                                    # distance
        row['p1_unf_err'] * (row['point_victor'] - 1) + row['p2_unf_err'] * (2 - row['point_victor']),      # error
    ]
    features.append(cur_list)

    if idx == 0:
        print(cur_list)

features = np.array(features)
slopes = np.array(df['slope'])

model = LinearRegression().fit(features, slopes)
print(f"Coefficients: {model.coef_}")
print(f"Score: {model.score(features, slopes)}")

momentum_gold = np.array(df['cum_flow'])

delta_momentum_pred = model.predict(features)

momentum_pred = []
for delta in delta_momentum_pred:
    if len(momentum_pred) == 0:
        momentum_pred.append(delta)
    else:
        momentum_pred.append(delta + momentum_pred[-1])
momentum_pred = np.array(momentum_pred)

x = np.array([i + 1 for i in range(len(slopes))])

plt.plot(x, momentum_gold)
plt.plot(x, momentum_pred)
plt.show()