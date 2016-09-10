import pandas as pd
import numpy as np
import seaborn as sns
plt = sns.plt
import json
import flash
with open('data/const_speed.json') as f:
    sensor_data = json.load(f)['sensor']
df = flash.to_df(sensor_data)
std_cutoff = 0.5
window_size = 5

gz = df['g_z'].rolling(window=window_size).mean()
gz_bin = 1.0 * (gz > std_cutoff * gz.std()) - (gz < -std_cutoff * gz.std())
gz_diff = gz_bin.diff().fillna(False)

"""
def rotate(x, y, degree):
    return (x * np.cos(degree) - y * np.sin(degree), x * np.sin(degree) + y * np.cos(degree))

xs, ys = ([], [])
(x, y) = (0, 0)
(dx, dy) = (0.2, 0)
for gz in df['g_z'].dropna():
    (dx, dy) = rotate(dx, dy, gz / 20000)
    x += 0.2 * dx
    y += 0.2 * dy
    xs.append(x)
    ys.append(y)

plt.plot(xs, ys)
"""
