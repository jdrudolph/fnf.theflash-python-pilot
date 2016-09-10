import pandas as pd
import numpy as np
import seaborn as sns
plt = sns.plt
import json

with open('sensor_data.json') as f:
    sensor_data = json.load(f)
df = pd.DataFrame.from_dict(sensor_data)
df['g_z'] = df['g'].str.get(2)


std_cutoff = 0.5
window_size = 10

gz = df['g_z'].rolling(window=window_size).mean()
gz_bin = 1.0 * (gz > std_cutoff * gz.std()) - (gz < -std_cutoff * gz.std())
gz_diff = gz_bin.diff().fillna(False)

