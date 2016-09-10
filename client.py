import pika
import json
import sys
from channelNames import ChannelNames
from messages import Messages


class Receiver:
    def __init__(self, onReceive):
        self.__onReceive = onReceive

    def callback(self, ch, method, properties, body):
        self.__onReceive(json.loads(body.decode('UTF-8')))


class Subscription:
    def __init__(self, name, onReceive):
        self.name = name
        self.onReceive = onReceive


class Client:
    def __init__(self, clientId, accessCode=None):
        self.__channelNames = ChannelNames(clientId)
        self.__messages = Messages(clientId, accessCode)
        self.__listeners = []
        self.__connected = False
        self.__connection = None
        self.__channel = None
        self.__clientId = clientId

    def __assertQueue(self, channelName):
        self.__channel.queue_declare(queue=channelName, durable=True)

    def __assertExchange(self, exchangeName):
        self.__channel.exchange_declare(exchange=exchangeName, type='direct')

    def __publishToExchange(self, exchangeName, routingKey, message):
        self.__assertExchange(exchangeName)
        self.__channel.basic_publish(exchange=exchangeName, routing_key=routingKey, body=message)

    def __publishToQueue(self, channelName, message):
        self.__channel.basic_publish(exchange="", routing_key=channelName, body=message)

    def __subscribe(self, exchangeName, routingKey, onReceive):
        receiver = Receiver(onReceive)
        self.__assertExchange(exchangeName)
        result = self.__channel.queue_declare(exclusive=True)
        queueName = result.method.queue
        self.__channel.queue_bind(exchange=exchangeName, queue=queueName, routing_key=routingKey)

        self.__channel.basic_consume(receiver.callback, queue=queueName, no_ack=True)

    def __addSubscriptions(self):
        for listener in self.__listeners:
            self.__subscribe(self.__clientId, listener.name, listener.onReceive)

    def connect(self, url):
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(url))
        self.__channel = self.__connection.channel()
        self.__connected = True
        self.__addSubscriptions()
        print("Connected.")

    def isConnected(self):
        return self.__connected

    def disconnect(self):
        self._connected = False;
        try:
            self.__connection.close()
        except ignored:
            pass

    def announce(self):
        self.__publishToQueue(self.__channelNames.announce(), self.__messages.announce())
        try:
            self.__channel.start_consuming()
        except KeyboardInterrupt:
            self.__channel.stop_consuming()

    def powerControl(self, powerValue):
        self.__publishToExchange(self.__clientId, "power", self.__messages.powerControl(powerValue))

    def onRaceStart(self, onReceive):
        name = self.__channelNames.raceStart()
        self.__listeners.append(Subscription(name, onReceive))

    def onRaceStop(self, onReceive):
        name = self.__channelNames.raceStop()
        self.__listeners.append(Subscription(name, onReceive))

    def onVelocity(self, onReceive):
        name = self.__channelNames.velocity()
        self.__listeners.append(Subscription(name, onReceive))

    def onPenalty(self, onReceive):
        name = self.__channelNames.penalty()
        self.__listeners.append(Subscription(name, onReceive))

    def onSensor(self, onReceive):
        name = self.__channelNames.sensor()
        self.__listeners.append(Subscription(name, onReceive))

    def onRoundPassed(self, onReceive):
        name = self.__channelNames.roundPassed()
        self.__listeners.append(Subscription(name, onReceive))
