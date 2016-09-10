import pandas as pd
import json
from pprint import pprint
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
%matplotlib qt

#X.) Define Constants / Variables
std_cutoff = 0.5
smoothing_window = 5

#1.) Load Data
filepath = '/home/marx/Documents/GitHubProjects/theflash/data/test_data/test_json.json'
with open(filepath) as data_file:
    data = json.load(data_file)

#2.) Convert to df
sensor_events = data['sensorEvents']
sensor_events_df = pd.DataFrame(sensor_events)
for sensor in ['a', 'g', 'm']:
    for i,dim in enumerate(['x', 'y', 'z']):
        sensor_events_df['{}_{}'.format(sensor,dim)] = sensor_events_df[sensor].str.get(i)

#3.) Get std
t_df = sensor_events_df['t']
g_z_df = sensor_events_df['g_z']
std_g_z = g_z_df.std()

#4.) Plot
initial_direction = 'right'
for p in range(0,len(g_z_df)):
    this_g_z = g_z_df[p]
    # if direction == 'right':
    #     this_x = p
    # elif direction == 'left':
    #     this_x = p-1
    # elif direction == 'top':
    #     this_x = last_p
    # elif direction == 'down':
    #     this_x = last_p
    if this_g_z > std_cutoff*std_g_z:
        plt.plot(p,1,'o')
    elif this_g_z < -std_cutoff*std_g_z:
        plt.plot(p,-1,'o')
    else:
        plt.plot(p,0,'o')
plt.show()

#5.) Get lin plot
track_lin = []
for p in range(0, len(g_z_df)):
    this_g_z = g_z_df[p]
    if this_g_z > std_cutoff*std_g_z or this_g_z < -std_cutoff*std_g_z: #Curve
        track_lin.append(2)
    else: #Without curve
        track_lin.append(0)
track_lin = pd.DataFrame(track_lin)


plt.plot(track_lin,'o')
plt.plot(track_lin.rolling(window=10).mean(),'o')
plt.show()

n_track_points = 200
this_range = track_lin[2000:2000+n_track_points]
corrs = []
for f in range(0,len(track_lin),1):
    if f > len(track_lin)-n_track_points:
        break
    cc = np.corrcoef(this_range[0].values,track_lin[f:f+n_track_points][0].values)
    corrs.append(cc[0,1])
track_lin[f:f+n_track_points][0].values.shape
this_range[0].values.shape
np.sum(np.array(corrs)==1)
plt.plot(corrs)
plt.plot(g_z_df)
plt.show()
plt.figure()

#TEST
