from client import Client
import os

config = {
        'TEAM_NAME' : 'theflash',
        'ACCESS_CODE' : 'züwermepa',
        'RABBIT_HOST' : 'localhost'
        }

 
powerValue = 120
client = Client(config['TEAM_NAME'], config['ACCESS_CODE'])
RABBIT_HOST = config['RABBIT_HOST']

from collections import defaultdict
msgs = defaultdict(lambda : [])
def receive(msg, event):
    msgs[event].append(msg)

def onRaceStart(msg):
    receive(msg, 'start')
    client.powerControl(powerValue)

def onVelocity(msg):
    receive(msg, 'velocity')
    client.powerControl(powerValue)


def onRoundPassed(msg):
    receive(msg, 'round')
    client.powerControl(powerValue)

def onRaceStop(msg):
    receive(msg, 'stop')
    client.disconnect()

import flash
from imp import reload
reload(flash)
flash_pilot = flash.Flash(client)

client.onRaceStart(flash_pilot.on_race_start)
client.onVelocity(flash_pilot.on_velocity)
client.onSensor(flash_pilot.on_sensor)
client.onPenalty(flash_pilot.on_penalty)
client.onRoundPassed(flash_pilot.on_round_passed)
client.onRaceStop(flash_pilot.on_race_stop)

client.connect(RABBIT_HOST)
client.announce()
