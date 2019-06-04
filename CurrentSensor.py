import RPi.GPIO as GPIO
import threading


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
	def __init__(self, Buttons):
		
		# Program is a dictionary of info, this will be passed into this variable.
		# It will hold the info for all 7 buttons which will include current limit data
		self.prog = Buttons

		self.currentData = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
		self.threadData = {}
		self.threadLock = threading.Lock()

	# This is the function that is called in the main program when a button is pressed. It 
	# creates a new thread for an internal function so that every button can run on a 
	# seperate thread. 
	def startRead(self, Button):
		try:
			newThread = threading.Thread( target = read, args = (Button, self.threadLock,) )
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
	def read(self, Button, lock):
		while (True):
			
			lock.acquire()

			#TODO: Read data from the adc

			# We store the data so that the GUI can display the data
			self.currentData[num] = adcReading

			lock.release()

			if (adcReading > self.prog[num]['MaxCurrent']):
				#TODO: throw exception back to the main
				# This should immediately interrupt any tasks at main and shut down 
				# the respective output. It should show a popup with the error.
				break


	# Getter method for the current data
	def getCurrent(self, Button):
		try:
			return self.currentData[Button]
		except Exception as e:
			return -1
