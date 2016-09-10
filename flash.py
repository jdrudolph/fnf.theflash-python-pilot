import pandas as pd

class Flash:
    def __init__(self, client, laps=0):
        self._client = client
        self._laps = laps
        
        self.sensor_data = []
        
        self.window_size = 0
        self.gz_std = 0

    def on_sensor(self, msg):
        if (self._laps <= 1):
            self._warmup(msg)
        if (self._laps > 1):
            self._mopsgeschwindigkeit(msg)

    def on_round_passed(self, msg):
        print('round passed')
        self._laps += 1
        self.gz_std = to_df(self.sensor_data)['g_z'].std()

    def _warmup(self, msg):
        self.sensor_data.append(msg)
        self._client.powerControl(80)

    def _mopsgeschwindigkeit(self, msg):
        gz = msg['g'][2] 
        is_corner = gz > self.gz_std or gz < -self.gz_std
        power = 40 if is_corner else 80
        if is_corner:
            print('corner!')
        self._client.powerControl(power)

def to_df(sensor_data):
    df = pd.DataFrame(sensor_data)
    for sensor in ['a', 'g', 'm']:
        for i,dim in enumerate(['x', 'y', 'z']):
            df['{}_{}'.format(sensor,dim)] = df[sensor].str.get(i)
    return df

