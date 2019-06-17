import RPi.GPIO as GPIO
import threading
import pigpio
import smbus2

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
	def __init__(self, Buttons, dataLock, I2CLock, GPIOObjects, bus):
		
		# Program is a dictionary of info, this will be passed into this variable.
		# It will hold the info for all 7 buttons which will include current limit data
		self.prog = Buttons

		self.currentData = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
		self.threadData = {}
		self.threadLock = dataLock
		self.I2CLock = I2CLock
		self.GPIOList = []
		self.GPIOList.extend(GPIOObjects)
		self.bus = bus

	# This is the function that is called in the main program when a button is pressed. It 
	# creates a new thread for an internal function so that every button can run on a 
	# seperate thread. 
	def startRead(self, Button):
		try:
			newThread = threading.Thread( target = read, args = (Button, self.threadLock, self.I2CLock, self.bus
				) )
			self.threadData[Button] = newThread
			self.threadData[Button].start()
		except Exception as e:
			raise e

	def stopRead(self, Button):
		try:
			self.threadData[Button].join()
		except Exception as e:
			raise e

	# This function begins the loop that reads the adc data and determines if the current is 
	# going over the set limit. If it is then 
	def read(self, Button, threadLock, I2CLock, bus):
		while (True):
			
			I2CLock.acquire()
			I2CSelect(Button + 1)
			# Read data from the adc
			adcReading = bus.read_i2c_block_data(0x54, 0, 2)
			I2CLock.release()

			# Convert adcReading into integer value
			readingValue = adcReading[0]
			readingValue += adcReading[1] << 2

			# We store the data so that the GUI can display the 
			dataLock.acquire()
			self.currentData[num] = readingValue
			dataLock.release()

			if (adcReading > self.prog[num]['MaxCurrent']):
				killChannel(Button)
				break

	def killChannel(self, Button):
		if Button < 3:
			self.GPIOList[Button].ChangeDutyCycle(0)
		else:
			tempDict = {3:18, 4:12, 5:19, 6:13}
			self.GPIOList[3].hardware_PWM(tempDict[Button], 0, 0)

	# Getter method for the current data
	def getCurrent(self, Button):
		try:
			return self.currentData[Button]
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
