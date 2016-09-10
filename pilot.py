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

msgs = []
def receive(msg):
    msgs.append(msg)

def onRaceStart(msg):
    print('race started')
    receive(msg)
    client.powerControl(powerValue)


def onVelocity(msg):
    receive(msg)
    client.powerControl(powerValue)


def onPenalty(msg):
    receive(msg)
    client.powerControl(powerValue)


def onRoundPassed(msg):
    receive(msg)
    client.powerControl(powerValue)


def onRaceStop(msg):
    receive(msg)
    client.disconnect()

from flash import Flash
flash_pilot = Flash(client)

client.onRaceStart(flash_pilot.on_race_start)
client.onVelocity(flash_pilot.on_velocity)
client.onSensor(flash_pilot.on_sensor)
client.onPenalty(onPenalty)
client.onRoundPassed(flash_pilot.on_round_passed)
client.onRaceStop(onRaceStop)

client.connect(RABBIT_HOST)
client.announce()

import json
with open('other_msgs.json', 'w') as f:
    json.dump(msgs, f)
