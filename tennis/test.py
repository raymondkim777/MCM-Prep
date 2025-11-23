import csv
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import datetime
import time
x = time.strptime('00:01:00,000'.split(',')[0],'%H:%M:%S')
datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
60.0


final_data = []
df = pd.read_csv('data/2024_Wimbledon_featured_matches.csv')

match_data = df[df['match_id'] == '2023-wimbledon-1701']
momentum_deltas = np.array([])  # momentum values derived from flow model

'''
Features:
- Serve: (-1)^{data['server'] - 1}
- Victor: (-1)^{data['point_victor'] - 1} * (1 + |data['server'] - data['point_victor']|)
- Ace: int(data['p1_ace'] + data['p2_ace'] > 0) * (-1)^{data['server'] - 1}
- Volley: data['rally_count'] * (-1)^{data['point_victor'] - 1}
- Distance: data['p2_distance_run'] - data['p1_distance_run']
- Error: data['p1_unf_err'] * (data['point_victor'] - 1) + data['p2_unf_err'] * (2 - data['point_victor'])
'''

