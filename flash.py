import json
import pandas as pd

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

    def on_sensor(self, msg):
        if (self._laps <= 1):
            self._warmup(msg)
        if (self._laps > 1):
            self._mopsgeschwindigkeit(msg)

    def on_round_passed(self, msg):
        print('round passed')
        self._laps += 1
        self.gz_std = to_df(self.sensor_data)['g_z'].std()
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

def to_df(sensor_data):
    df = pd.DataFrame(sensor_data)
    for sensor in ['a', 'g', 'm']:
        for i,dim in enumerate(['x', 'y', 'z']):
            df['{}_{}'.format(sensor,dim)] = df[sensor].str.get(i)
    return df

