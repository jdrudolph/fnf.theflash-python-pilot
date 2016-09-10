class ChannelNames:
    def __init__(self, clientId):
        self.__clientId = clientId

    def raceStart(self):
        return "start"

    def raceStop(self):
        return "stop"

    def sensor(self):
        return "sensor"

    def velocity(self):
        return "velocity"

    def penalty(self):
        return "penalty"

    def roundPassed(self):
        return "roundtime"

    def announce(self):
        return "/app/pilots/announce"

    def powerControl(self):
        return "power"
