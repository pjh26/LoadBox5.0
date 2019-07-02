import RPi.GPIO as GPIO
import threading
import pigpio
import smbus
import Queue

#set GPIO to BCM numbering scheme. Pin numbering can be found at pinout.xyz
GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.OUT)	# IS_0
GPIO.setup(19, GPIO.OUT)	# IS_1
GPIO.setup(13, GPIO.OUT)	# IS_2

'''

* This class will monitor current data given by an ADC on the switch box 4.0 board
* if it reads above a certain point then it will immediately shut off that gpio and
* send an alert to main
*
* The goal is for this to run on a seperate thread any time that the switch page opens.
* For now it will poll to check for currents as there is probably not a good way to
* use interrupts for current limiting

'''
class CurrentSensor:
	def __init__(self, Buttons, I2CLock, bus, CurrentQueueList):

		# Program is a dictionary of info, this will be passed into this variable.
		# It will hold the info for all 7 buttons which will include current limit data
		self.prog = Buttons

		self.currentData = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
		self.I2CLock = I2CLock
		self.bus = bus
		self.QueueList = []
		self.QueueList.extend(CurrentQueueList)
		self.threadData = []
		self.stopQueueList = []
		self.tempDict = {0:20, 1:23, 2:24, 3:18, 4:12, 5:19, 6:13}

		for i in range(7):
			self.stopQueueList.append(Queue.Queue(1))
			self.threadData.append(threading.Thread( target = self.read, args = (i, self.I2CLock, self.bus, self.QueueList[i], self.stopQueueList[i])))


	# This is the function that is called in the main program when a button is pressed. It
	# creates a new thread for an internal function so that every button can run on a
	# seperate thread.
	def startRead(self):
		try:
			for i in range(7):
				self.stopQueueList[i].get(False)
				self.threadData[i].start()
		except Exception as e:
			pass

	def stopRead(self):
		try:
			for i in range(7):
				self.stopQueueList[i].put(False)
				self.threadData[i].join()
		except Exception as e:
			pass

	# This function begins the loop that reads the adc data and determines if the current is
	# going over the set limit. If it is then
	def read(self, ButtonNum, I2CLock, bus, Queue, stopQueue):
		while (True):
			I2CLock.acquire()
			I2CSelect(ButtonNum + 1)
			# Read data from the adc
			adcReading = bus.read_i2c_block_data(0x54, 0, 2)
			I2CLock.release()

			# Convert adcReading into integer value
			readingValue = adcReading[0] + (adcReading[1] << 2)
			if (adcReading > self.prog[num]['MaxCurrent']):
				GPIO.output(tempDict[num], 0)

			if Queue.empty():
				try:
					Queue.put(readingValue, False)
				except Exception as e:
					raise e

			if stopQueue.full():
				break


	# Getter method for the current data
	def getCurrent(self, ButtonNum):
		try:
			return self.currentData[ButtonNum]
		except Exception as e:
			return -1

	def I2CSelect(self, num):
		if (num == 0):
			GPIO.output(26, 0)
			GPIO.output(19, 0)
			GPIO.output(13, 0)
		elif (num == 1):
			GPIO.output(26, 1)
			GPIO.output(19, 0)
			GPIO.output(13, 0)
		elif (num == 2):
			GPIO.output(26, 0)
			GPIO.output(19, 1)
			GPIO.output(13, 0)
		elif (num == 3):
			GPIO.output(26, 1)
			GPIO.output(19, 1)
			GPIO.output(13, 0)
		elif (num == 4):
			GPIO.output(26, 0)
			GPIO.output(19, 0)
			GPIO.output(13, 1)
		elif (num == 5):
			GPIO.output(26, 1)
			GPIO.output(19, 0)
			GPIO.output(13, 1)
		elif (num == 6):
			GPIO.output(26, 0)
			GPIO.output(19, 1)
			GPIO.output(13, 1)
		elif (num == 7):
			GPIO.output(26, 1)
			GPIO.output(19, 1)
			GPIO.output(13, 1)
