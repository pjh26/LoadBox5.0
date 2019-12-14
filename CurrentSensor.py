import RPi.GPIO as GPIO
import threading
import pigpio
import smbus
import queue
import random

#set GPIO to BCM numbering scheme. Pin numbering can be found at pinout.xyz
GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.OUT)	# IS_0
GPIO.setup(26, GPIO.OUT)	# IS_1
GPIO.setup(4, GPIO.OUT) 	# IS_2


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
			self.stopQueueList.append(queue.Queue(1))
			self.threadData.append(threading.Thread( target = self.read, args = (i, self.I2CLock, self.bus, self.QueueList[i], self.stopQueueList[i])))


	# This is the function that is called in the main program when a button is pressed. It
	# creates a new thread for an internal function so that every button can run on a
	# seperate thread.
	def startRead(self, btn = -1):
		if btn == -1:
			for i in range(7):
				try:
					self.threadData[i].start()
					self.stopQueueList[i].get(False)
				except Exception as e:
					pass
		else:
			try:
				self.threadData[btn].start()
				self.stopQueueList[btn].get(False)
			except Exception as e:
				pass

	def stopRead(self, btn = -1):
		if btn == -1:
			for i in range(7):
				try:
					self.stopQueueList[i].put(False)
					self.threadData[i].join()
				except Exception as e:
					pass
		else:
			try:
				self.stopQueueList[num].put(False)
				self.threadData[num].join()
			except Exception as e:
				pass

	# This function begins the loop that reads the adc data and determines if the current is
	# going over the set limit. If it is then
	def read(self, ButtonNum, I2CLock, bus, Queue, stopQueue):
		maxCur = self.prog[ButtonNum]['MaxCurrent']
		GPIOnum = self.tempDict[ButtonNum]
		while (True):

			I2CLock.acquire()
			self.I2CSelect(ButtonNum + 1)

			# Read data from the adc
			adcReading = bus.read_i2c_block_data(84, 0, 2)

			I2CLock.release()

			# Convert adcReading into integer value
			total = 0
			for i in range(10):
				total += adcReading[1] + (adcReading[0] << 8)

			current = 0.003*(total/10) - 1.2202

			if (current > float(maxCur)):
				GPIO.output(GPIOnum, 0)


			if not Queue.full():
				try:
					Queue.put(current, False)
				except Exception as e:
					pass

			if stopQueue.full():
				break


	# Getter method for the current data
	def getCurrent(self, ButtonNum):
		try:
			return '%.1f'%(abs(self.QueueList[ButtonNum].get(False)))
		except Exception as e:
			return -1

	def I2CSelect(self, num):
		if (num == 0):
			GPIO.output(21, 0)
			GPIO.output(26, 0)
			GPIO.output(4, 0)
		elif (num == 1):
			GPIO.output(21, 1)
			GPIO.output(26, 0)
			GPIO.output(4, 0)
		elif (num == 2):
			GPIO.output(21, 0)
			GPIO.output(26, 1)
			GPIO.output(4, 0)
		elif (num == 3):
			GPIO.output(21, 1)
			GPIO.output(26, 1)
			GPIO.output(4, 0)
		elif (num == 4):
			GPIO.output(21, 0)
			GPIO.output(26, 0)
			GPIO.output(4, 1)
		elif (num == 5):
			GPIO.output(21, 1)
			GPIO.output(26, 0)
			GPIO.output(4, 1)
		elif (num == 6):
			GPIO.output(21, 0)
			GPIO.output(26, 1)
			GPIO.output(4, 1)
		elif (num == 7):
			GPIO.output(21, 1)
			GPIO.output(26, 1)
			GPIO.output(4, 1)
