import json
import pandas as pd
import numpy as np

class Flash:
    def __init__(self, client, laps=0):
        self._client = client
        self._laps = laps
        
        self.sensor_data = []
        
        self.window_size = 0
        self.gz_std = 0

        self._last_gate_time = float('NaN')
        self._section_time = float('NaN')
        self._velocity = float('NaN')

        self._all_gz = None # set after warmup
        self._last_gz = None # set after warmup

        self.n_points_tracked = 150

    def on_sensor(self, msg):
        if (self._laps <= 1):
            self._warmup(msg)
        if (self._laps > 1):
            self._flashgeschwindigkeit(msg)

    def on_round_passed(self, msg):
        print('round passed')
        self._laps += 1
        if self._laps > 1:
            df = to_df(self.sensor_data)
            self.sensor_data = []
            self.gz_std = df['g_z'].std()
            self._all_gz = 2 * (df['g_z'] > self.gz_std) - 2 * (df['g_z'] < -self.gz_std)
            self._all_gz_smooth = pd.Series(df['g_z']).rolling(window=5).mean().values
            if (self._last_gz is None):
                self._last_gz = self._all_gz_smooth[-self.n_points_tracked:]
            print('round calc finished')
            with open('sensor_data_{}.json'.format(self._laps), 'w') as f:
                json.dump(self.sensor_data, f)

    def on_velocity(self, msg):
        self._velocity = msg['velocity']
        new_gate_time = msg['timeStamp']
        self._section_time = new_gate_time - self._last_gate_time
        self._last_gate_time = new_gate_time

    def on_race_start(self, msg):
        print('start race')

    def _warmup(self, msg):
        msg['v'] = self._velocity
        msg['section_time'] = self._section_time
        self._section_time = float('NaN')
        self.sensor_data.append(msg)
        self._client.powerControl(120)

    def _mopsgeschwindigkeit(self, msg):
        gz = msg['g'][2] 
        is_corner = gz > self.gz_std or gz < -self.gz_std
        power = 140 if is_corner else 120
        self._client.powerControl(power)

    def _flashgeschwindigkeit(self, msg):
        self.sensor_data.append(msg)
        gz = msg['g'][2]
        self._last_gz = np.append(self._last_gz, gz)[1:]
        all_gz = self._all_gz_smooth
        n = self.n_points_tracked
        step = 1
        ccs = [np.corrcoef(self._last_gz, 
            np.take(all_gz, range(0+k, n+k), mode='wrap'))[1,0]
        for k in range(0, len(all_gz), step)]
        self._point_in_track = np.nanargmax(ccs)
        if np.nanmax(ccs) > 0.8:
            print(self._point_in_track)
        

def to_df(sensor_data):
    df = pd.DataFrame(sensor_data)
    for sensor in ['a', 'g', 'm']:
        for i,dim in enumerate(['x', 'y', 'z']):
            try:
                df['{}_{}'.format(sensor,dim)] = df[sensor].str.get(i)
            except KeyError:
                print("couldn't find", sensor, dim)
                continue
    return df

