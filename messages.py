import json
import time

class Messages:
	
	def __init__(self, teamId, accessCode):
		self.__teamId = teamId
		self.__accessCode = accessCode

	def announce(self):
		return json.dumps({ \
			"teamId": self.__teamId, \
			"accessCode": self.__accessCode, \
			"optionalUrl": None, \
			"timestamp": time.time() \
  	})

	def powerControl(self, powerValue):
		return json.dumps({ \
			"p": powerValue, \
			"teamId": self.__teamId, \
			"accessCode": self.__accessCode, \
			"timeStamp": time.time() \
  	})
