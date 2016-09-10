import os
import sys
import json
import time
import pandas as pd
import numpy as np

from collections import defaultdict

class Flash:
    def __init__(self, client):
        self._client = client
        self._laps = 0

        self.msgs = defaultdict(lambda : [])
        
        self.extreme = 300.0

        self.power = 120

        self.memory = []
        self._remove_in_beginning = 50

    def receive(self, msg, event):
        self.msgs[event].append(msg)

    def on_sensor(self, msg):
        self.receive(msg, 'sensor')
        last = 'N'
        if len(self.memory) > 0:
            last = self.memory[-1]
        gz = msg['g'][2]
        if (abs(gz) > self.extreme):
            self.extreme = gz
        if (gz > 0.25 * self.extreme):
            if (last != 'R'):
                sys.stdout.write('R')
                self.memory.append('R')
        elif (gz < -0.25 * self.extreme):
            if (last != 'L'):
                sys.stdout.write('L')
                self.memory.append('L')
        else:
            if (last != 'G'):
                sys.stdout.write('G')
                self.memory.append('G')
        sys.stdout.flush()
        self._warmup(msg)
        """
        if (self._laps <= 1):
            self._warmup(msg)
        if (self._laps > 1):
            self._flashgeschwindigkeit(msg)
        """

    def on_round_passed(self, msg):
        self.receive(msg, 'round')
        self._laps += 1

    def on_velocity(self, msg):
        self.power += 1
        self.receive(msg, 'velocity')

    def on_race_start(self, msg):
        self.receive(msg, 'start')

    def on_race_stop(self, msg):
        self.receive(msg, 'stop')
        self._client.disconnect()
        with open(os.path.join('data','{}.json'.format(time.strftime('%Y-%m-%d-%H-%M'))), 'w') as f:
            json.dump(self.msgs, f)
   
    def on_penalty(self, msg):
        self.receive(msg, 'penalty')
        self._client.powerControl(100)

    def _warmup(self, msg):
        self._client.powerControl(self.power)

    def _mopsgeschwindigkeit(self, msg):
        gz = msg['g'][2] 
        is_corner = gz > self.gz_std or gz < -self.gz_std
        power = 140 if is_corner else 120
        self._client.powerControl(power)

    """
    def _flashgeschwindigkeit(self, msg):
        self.sensor_data.append(msg)
        gz = msg['g'][2]
        self._last_gz = np.append(self._last_gz, gz)[1:]
        all_gz = self._all_gz_smooth
        n = self.n_points_tracked
        step = 1
        ccs = [np.corrcoef(self._last_gz, np.take(all_gz, range(0+k, n+k), mode='wrap'))[1,0]
        for k in range(0, len(all_gz), step)]
        self._point_in_track = np.nanargmax(ccs)
        if np.nanmax(ccs) > 0.8:
            print(self._point_in_track)
    """  

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

