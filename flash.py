import os
import sys
import json
import time
import pandas as pd
import numpy as np
import seaborn as sns
plt = sns.plt

from collections import defaultdict

import re
rec_regex = re.compile(r'(.+?)\1+')

class Flash:
    def __init__(self, client):
        self._client = client
        self._laps = 0

        self.msgs = defaultdict(lambda : [])
        
        self.extreme = 300.0

        self.power = 130

        self.memory = []
        self.match = []
        self._remove_in_beginning = 100
        self.track = []
        self.lengths = []
        self.g_z = [0] * 5

        self._min = ""

        self._enter_t, self._enter_v = (0.0, 0.0)

        self._was_in_curve = False

    def receive(self, msg, event):
        self.msgs[event].append(msg)

    def memorize(self, segment):
        last = 'N'
        if len(self.memory) > 0:
            last = self.memory[-1]
            self.track, freq = find_track(self.memory)
            if len(self.track) > len(self.lengths):
                self.lengths = [0] * len(self.track)
            errors = find_position(self.track, self.memory)
            try:
                min_new = min(errors, key=lambda x : x[1])[3]
                if min_new != self._min:
                    self._min = min_new
                if len(self.memory) < 50:
                    print(self.track, freq)
                else:
                    print(self.track, ''.join(self.memory[-50:]))
                print(' '.join([''] * (min_new - 0)), '^')
            except ValueError:
                pass
        if (last != segment):
            if self._remove_in_beginning > 0:
                self._remove_in_beginning -= 1
            else:
                self.memory.append(segment)
                print(segment)

    def on_sensor(self, msg):
        self.receive(msg, 'sensor')
        gz = msg['g'][2]
        #gz_scaled = gz / self.extreme
        #print(' '* int(np.round((1 - gz_scaled) * 30)), gz)
        self.g_z = self.g_z[:-1]+[gz]
        mean_gz = np.mean(self.g_z)
        t = msg['timeStamp']
        plt.plot(gz, t)
        plt.plot(mean_gz, t)
        if (abs(mean_gz) > self.extreme):
            self.extreme = gz
        if (mean_gz > 0.1 * self.extreme):
            self.memorize('R')
            self.power = 150
            self._was_in_curve = True
        elif (mean_gz < -0.1 * self.extreme):
            self.memorize('L')
            self.power = 150
            self._was_in_curve = False
        else:
            self.memorize('G')
        sys.stdout.flush()
        if len(self.track) < 10:
            self._warmup(msg)
        else:
            print('flashgesch')
            self._flashgeschwindigkeit(msg)

    def on_round_passed(self, msg):
        self.receive(msg, 'round')
        self._laps += 1

    def on_velocity(self, msg):
        errors = find_position(self.track, self.memory)
        print('gate')
        try:
            position = min(errors, key=lambda x : x[1])
            print(position)
            if position[1] < 5:
                if self._was_in_curve:
                    print('enter', msg['timeStamp'], msg['velocity'])
                    self._enter_t = msg['timeStamp']
                    self._enter_v = msg['velocity']
                    self._was_in_curve = False
                elif len(self.track) >  0:
                    print('exit', msg['timeStamp'], msg['velocity'])
                    t1, t2 = self._enter_t, msg['timeStamp']
                    v1, v2 = self._enter_v, msg['velocity']
                    if (t2 - t1) == 0:
                        print('----------ZERO------------------set length', position[2]-1, length)
                    else:
                        length = (v1 + v2) / 2 * (t2 - t1)
                        print('----------------------------set length', position[2]-1, length)
                        self.lengths[position[2]-1] = length
        except ValueError:
            pass
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
        self._client.powerControl(120)

    def _warmup(self, msg):
        if len(self.memory) > 0 and self.memory[-1] == 'G':
            self.power = 155
        self._client.powerControl(self.power)
        gz = msg['g'][2] 
        #is_corner = gz > self.gz_std or gz < -self.gz_std
        #power = 140 if is_corner else 120

    def _flashgeschwindigkeit(self, msg):
        segment = self.memory[-1]
        v0 = self._enter_v
        t0 = self._enter_t
        t1 = msg['timeStamp']
        dt = t1 - t0
        if segment == 'G':
            position = self._min
            segment_length = self.lengths[position]
            if v0 != 0:
                t_g = segment_length / v0
                print(segment, position, segment_length, t_g, dt)
                if dt < 0.10 * t_g:
                    print("FLAAAASSSSHHH!!!!")
                    self._client.powerControl(250)
            else:
                print("Hit the breaks!")
                self._client.powerControl(140)

            

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


def find_position(track, memory):
    n = len(track)
    double_track = track + track + track + track
    position_track = [double_track[i:i+n] for i in range(0, n)]
    errors = []
    for i,position in enumerate(position_track):
        error = 0
        for a,b in zip(position, memory[-n:]):
            if a != b:
                error += 1
        errors.append((position, error, i, (i + n - 1) % n))
    return errors

import itertools
import collections
def find_track(memory):
    best_hits = []
    for k in range(10,20):
        slices = [memory[i:i+k] for i in range(0,len(memory)-k)]
        track_freq = collections.defaultdict(lambda : 0)
        has_value = False
        for s1,s2 in itertools.combinations(slices,2):
            if s1 == s2:
                track_freq[''.join(s1)] += 1
                has_value = True
        if has_value:
            try:
                best_hits.append(max(track_freq.items(), key=lambda x : x[1]))
            except:
                pass
    if len(best_hits) == 0:
        return "", 0
    return best_hits[-1]
