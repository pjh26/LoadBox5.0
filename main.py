from kivy.app import App
#kivy.require("1.8.0")
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.graphics import Line
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import mainthread
from smbus2 import SMBus
import shelve
import pigpio
import atexit
import RPi.GPIO as GPIO
import spidev
import CurrentSensor
import math
import threading
import random
import time
import Queue


#-------------------------------------------------------------------------------#
#                                                                               #
#     Code structure is documented in OneNote under User Interface Design       #
#                                                                               #
#-------------------------------------------------------------------------------#

#reset GPIO pin functions at exit of program
atexit.register(GPIO.cleanup)

#set GPIO to BCM numbering scheme. Pin numbering can be found at pinout.xyz
GPIO.setmode(GPIO.BCM)

#Configure kivy
Config.set('modules','cursor','1')

Config.write()


#-------------------------------------------------------------------------------#
#                                                                               #
#    Outputs are as follows          SPI Select            Slew Rate FB         #
#                                       CS0 - GPIO22          SR1 - GPIO05      #
#       Signal 1 - GPIO20               CS1 - GPIO27          SR2 - GPIO06      #
#       Signal 2 - GPIO23               CS2 - GPIO17                            #
#       Signal 3 - GPIO24                                                       #
#       Signal 4 - GPIO18            I2C Select                                 #
#       Signal 5 - GPIO12               IS0 - GPIO21                            #
#       Signal 6 - GPIO19               IS1 - GPIO26                            #
#       Signal 7 - GPIO13               IS2 - GPIO04                            #
#                                                                               #
#-------------------------------------------------------------------------------#



#initialize software pwm
#btn0
GPIO.setup(20, GPIO.OUT)
p0 = GPIO.PWM(20, 1)
p0.start(0)

#btn1
GPIO.setup(23, GPIO.OUT)
p1 = GPIO.PWM(23, 1)
p1.start(0)

#btn2
GPIO.setup(24, GPIO.OUT)
p2 = GPIO.PWM(24, 1)
p2.start(0)


#initialize hardware PWM for channels 3, 4, 5, and 6
GPIO.setup(18, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
hardPWM = pigpio.pi()

#initialize SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000

# Initialize select outputs
GPIO.setup(17, GPIO.OUT)	# CS2
GPIO.output(17, 0)

GPIO.setup(27, GPIO.OUT)	# CS1
GPIO.output(27, 0)

GPIO.setup(22, GPIO.OUT)	# CS0
GPIO.output(22, 0)

bus = SMBus(1)

def SPISelect(num):
	if (num == 0):
		GPIO.output(22, 0)
		GPIO.output(27, 0)
		GPIO.output(17, 0)
	elif (num == 1):
		GPIO.output(22, 1)
		GPIO.output(27, 0)
		GPIO.output(17, 0)
	elif (num == 2):
		GPIO.output(22, 0)
		GPIO.output(27, 1)
		GPIO.output(17, 0)
	elif (num == 3):
		GPIO.output(22, 1)
		GPIO.output(27, 1)
		GPIO.output(17, 0)
	elif (num == 4):
		GPIO.output(22, 0)
		GPIO.output(27, 0)
		GPIO.output(17, 1)
	elif (num == 5):
		GPIO.output(22, 1)
		GPIO.output(27, 0)
		GPIO.output(17, 1)
	elif (num == 6):
		GPIO.output(22, 0)
		GPIO.output(27, 1)
		GPIO.output(17, 1)
	elif (num == 7):
		GPIO.output(22, 1)
		GPIO.output(27, 1)
		GPIO.output(17, 1)
	else:
		GPIO.output(22, 0)
		GPIO.output(27, 0)
		GPIO.output(17, 0)

class HomeScreen(Screen):
	# Sets the value at the 'del' position in the dict to a value that represents 
	# either the choose program, delete program, or edit program function
	# param: func: the value (either 0,1,2) that globalData['del'] will be set to
	def setFunc(self, func):
		s = shelve.open('TestBoxData.db')

		#get a temporary copy of the dictionary stored in the shelve database
		globalData = s['global']
		globalData['del'] = func
		s['global'] = globalData
		s.close()

# ProgButton defines a custom button. For the most part it is identical to a normal 
# button but it allows us to more easily define a button for each individual program
class ProgButton(Button):
	def __init__(self, **kwargs):
		Button.__init__(self, **kwargs)

	# This function is called when buttons in chooseprog screen are pressed
	# and it returns the name of the screen that will be linked to next
	def getScrn(self):
		s = shelve.open('TestBoxData.db')

		#get a temporary copy of the dictionary stored in the shelve database
		globalData = s['global']
		#globalData['btn'] is the number of the button in chooseprog screen that called this function
		btn = globalData['btn']

		# Only update globalData['pos'] if it is NOT on the delete screen
		if not (globalData['del'] == 2):
			globalData['pos'] = btn

		# The choose program screen is used for both the edit and switches, so we have 
		# to determine what mode chooseprog screen is currently in
		if globalData['del'] == 2:
			scrn = 'chooseprog'
		elif globalData['del'] == 1:
			scrn = 'editprog'
		else:
			scrn = 'switch'
		#save the temporary copy of the dictionary back to the shelve dictionary
		s['global'] = globalData
		s.close()
		return scrn

# ChooseProgScreen defines the screen that allows the user to select which program
# they are going to test/edit/delete. 
class ChooseProgScreen(Screen):

	# This function is called any time we enter the choose prog screen. It first clears
	# all widgets then updates the buttons and labels to reflect their current state
	def updateButtons(self):
		self.ids.chooseProgGrid.clear_widgets()

		self.ids.lblTitle.text = self.getLblTxt()
		i = 1
		# Creating multiple instances of an object. REF https://stackoverflow.com/questions/30099915/can-i-define-a-widget-in-a-kv-file-and-reference-it-in-a-py-file
		# Iterate through the program dictionary and create a button for each program
		while True:
			btnText = self.getBtnTxt(i)
			if btnText != "error":
				self.newButton = ProgButton(id = str(i), text = btnText)
				self.newButton.bind(on_press = self.popOpen)
				self.ids.chooseProgGrid.add_widget(self.newButton)
			else:
				break
			i += 1

	# returns the title of the current program to be the title of the corresponding button
	# parameters: btn: the number of the current button whose title is to be returned
	def getBtnTxt(self, btn):
		s = shelve.open('TestBoxData.db')

		#get a temporary copy of the dictionary stored in the shelve database
		progData = s['data']
		if btn in progData:
			text = progData[btn]['title']
		else:
			text = "error"
		s.close()
		return text

	#returns the appropriate title based on the number at the 'del' position in the dict
	#returns a title for either the choose program screen, the Edit program screen or the Delete program screen
	def getLblTxt(self):
		s = shelve.open('TestBoxData.db')

		#get a temporary copy of the dictionary stored in the shelve database
		globalData = s['global']

		#check what mode chooseprog screen is in and set 'title' variable based on that
		if globalData['del'] == 0:
			title = 'Choose Program'
		elif globalData['del'] == 1:
			title = 'Choose Program to Edit'
		elif globalData['del'] == 2:
			title = 'Choose Program to Delete'
		s.close()
		return title

	#called in the delete program screen
	#deletes one program's information from the dictionary and shifts the subsequent programs back one position
	def setFunc(self):
		s = shelve.open('TestBoxData.db')

		#get a temporary copy of the global data stored in the shelve database
		globalData = s['global']

		# Get a temporary copy of the program data dictionary in the shelve database
		progData = s['data']

		#get the number of the current program
		btn = globalData['btn']

		#check if the chooseprog screen is in delete mode
		if globalData['del'] == 2:
			if btn in progData:
				# Delete the current program information and shift all the subsequent
				# programs back one position.
				del progData[btn]
				for i in range(btn,len(progData)+1):
					if (i + 1) in progData:
						progData[i] = progData.pop(i+1)

				#decrement the current program variable
				globalData['pos'] = globalData['pos'] - 1
				globalData['maxpos'] = globalData['maxpos'] - 1
		s['global'] = globalData
		s['data'] = progData
		s.close()

	#called when the buttons in chooseprog screen are pressed
	#only opens popup if chooseprog screen is in delete mode
	def popOpen(self, btn):
		s = shelve.open('TestBoxData.db')
		#get a temporary copy of the dictionary stored in the shelve database
		globalData = s['global']

		#check if chooseprog screen is in delete mode
		if globalData['del'] == 2:
			#open popup
			self.popup.open()

		#each button in chooseprog screen calls this function with a different number between 1-24
		#gloablData['btn'] is set to the number of the button that called this function when it was pressed
		globalData['btn'] = int(btn.id)
		s['global'] = globalData
		s.close()

class SwitchScreen(Screen):

	def __init__(self, **kwargs):
		Screen.__init__(self, **kwargs)
		self.slewRateList = []
		for i in range(128):
			self.slewRateList.append(0)
		self.GPIOList = []
		self.GPIOList.append(p0)
		self.GPIOList.append(p1)
		self.GPIOList.append(p2)
		self.GPIOList.append(hardPWM)

	def getSlideValue(self, slideVal):
		return str(self.slewRateList[int(slideVal)]) + " V/us"

	#this updates the buttons upon entering the screen to reflect their current state
	def updateScreen(self):

                self.btnList = []
                self.btnList.append(self.ids.btn0)
                self.btnList.append(self.ids.btn1)
                self.btnList.append(self.ids.btn2)
                self.btnList.append(self.ids.btn3)
                self.btnList.append(self.ids.btn4)
                self.btnList.append(self.ids.btn5)
                self.btnList.append(self.ids.btn6)

                self.btnFuncList = []
                self.btnFuncList.append(self.ids.btn0func)
                self.btnFuncList.append(self.ids.btn1func)
                self.btnFuncList.append(self.ids.btn2func)
                self.btnFuncList.append(self.ids.btn3func)
                self.btnFuncList.append(self.ids.btn4func)
                self.btnFuncList.append(self.ids.btn5func)
                self.btnFuncList.append(self.ids.btn6func)

                self.btnFrqList = []
                self.btnFrqList.append(self.ids.btn0frq)
                self.btnFrqList.append(self.ids.btn1frq)
                self.btnFrqList.append(self.ids.btn2frq)
                self.btnFrqList.append(self.ids.btn3frq)
                self.btnFrqList.append(self.ids.btn4frq)
                self.btnFrqList.append(self.ids.btn5frq)
                self.btnFrqList.append(self.ids.btn6frq)

                self.btnDCList = []
                self.btnDCList.append(self.ids.btn0dc)
                self.btnDCList.append(self.ids.btn1dc)
                self.btnDCList.append(self.ids.btn2dc)
                self.btnDCList.append(self.ids.btn3dc)
                self.btnDCList.append(self.ids.btn4dc)
                self.btnDCList.append(self.ids.btn5dc)
                self.btnDCList.append(self.ids.btn6dc)

                self.myPopup = Popup(title="Loading...", size_hint=(0.6, 0.1), auto_dismiss=False)
                self.progBar = ProgressBar(max=127)

                self.myPopup.add_widget(self.progBar)

		s = shelve.open('TestBoxData.db')

		# Get a temporary copy of the global data dictionary stored in the shelve database
		globalData = s['global']

		# Get a temporary copy of the program data dictionary in the shelve database
		progData = s['data']

		#globalData['pos'] is the current program variable
		pos = globalData['pos']

		#update screen title
		self.ids.switchtitle.text = str(progData[pos]['title'])

		#update buttons
		for i in range(7):
			self.btnList[i].text = str(progData[pos]['buttons'][i]['title'])
			self.btnList[i].state = "normal"

			self.btnFuncList[i].text = str(progData[pos]['buttons'][i]['func'])
			if progData[pos]['buttons'][i]['func'] == 'PWM':
				self.btnFrqList[i].text = str(progData[pos]['buttons'][i]['frq']) + ' Hz'
				self.btnDCList[i].text = str(progData[pos]['buttons'][i]['dc']) + "% dc"
			else:
				self.btnFrqList[i].text = ""
				self.btnDCList[i].text = ""

		# Now we need to start the current sensors. We want one thread per sensor to maximize speed

		buttonData = progData[globalData['pos']]['buttons']
		self.I2CLock = threading.Lock()

		self.CurrentQueueList = []
		for i in range(7):
			self.CurrentQueueList.append(Queue.LifoQueue(2))

		# CurrentSensor:
		#		@params: buttonData   - Dictionary of data containing the functions of each button
		#				 I2CLock      - ThreadLock object to prevent collisions on the I2C bus
		#				 GPIOList	  - List of all of the GPIO objects that output functions
		#				 bus 		  - SMBus object for I2C communication
		#				 CurrentQueue - LIFO Queue that will be used for displaying the measured current values
		self.curSensor = CurrentSensor.CurrentSensor(buttonData, self.I2CLock, bus, self.CurrentQueueList)
		self.curSensor.startRead()

		s.close()

	# Called when the back button is pressed
	# Stops PWM outputs on leaving the switch screen and makes sure that all current sensor
	# threads are joined/killed
	def stopPWM(self):
		p0.ChangeDutyCycle(0)
		p1.ChangeDutyCycle(0)
		p2.ChangeDutyCycle(0)
		hardPWM.hardware_PWM(18,0,0)
		hardPWM.hardware_PWM(12,0,0)
		hardPWM.hardware_PWM(19,0,0)
		hardPWM.hardware_PWM(13,0,0)

	def cleanUP(self):
		self.curSensor.stopRead()
		self.stopPWM()

	#get button dc, frq to display below button
	def getbtnInfo(self,btn):
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']

		pos = globalData['pos']
		if btn in progData:
			dc =str(progData[pos]['buttons'][btn]['dc'])
			frq =str(progData[pos]['buttons'][btn]['frq'])
		else:
			dc = frq = ""
		btnInfo = [frq,dc]
		s.close()
		return btnInfo

	#send new value to potentiometer via SPI bus
	def updatePot(self):
		intVal = int(self.ids.slide.value)
		if self.ids.togbtn0.state == "down":
			SPISelect(1)
		elif self.ids.togbtn1.state == "down":
			SPISelect(2)
		elif self.ids.togbtn2.state == "down":
			SPISelect(3)
		elif self.ids.togbtn3.state == "down":
			SPISelect(4)
		elif self.ids.togbtn4.state == "down":
			SPISelect(5)
		elif self.ids.togbtn5.state == "down":
			SPISelect(6)
		elif self.ids.togbtn6.state == "down":
			SPISelect(7)
		else:
			SPISelect(0)
		spi.writebytes(intVal)
		SPISelect(0)

	def loadingPopup(self, open_close):
		if open_close:
			self.myPopup.open()
		else:
			self.myPopup.dismiss()
	@mainthread
	def updateProgBar(self, val):
		self.progBar.value = val

	def I2C_ERROR(self):
		GPIO.setup(25, GPIO.OUT)
		GPIO.output(25, 1)
		time.sleep(0.5)
		GIO.output(25, 0)
		GPIO.cleanup(25)

	#determine and display slew rate on selected channel
	def testSlewRate(self):
		SRList = []
		if self.ids.togbtn0.state == "down":
			SRList = self.getSlewRateSpectrum(1)
		elif self.ids.togbtn1.state == "down":
			SRList = self.getSlewRateSpectrum(2)
		elif self.ids.togbtn2.state == "down":
			SRList = self.getSlewRateSpectrum(3)
		elif self.ids.togbtn3.state == "down":
			SRList = self.getSlewRateSpectrum(4)
		elif self.ids.togbtn4.state == "down":
			SRList = self.getSlewRateSpectrum(5)
		elif self.ids.togbtn5.state == "down":
			SRList = self.getSlewRateSpectrum(6)
		elif self.ids.togbtn6.state == "down":
			SRList = self.getSlewRateSpectrum(7)
		else:
			for i in range(128):
				SRList.append(0)
		self.slewRateList = SRList
		self.stopPWM()
		self.loadingPopup(False)

	# This function tests every single potentiometer possibility to give the tester an idea of
	# what slew rates they will be able to us
	def getSlewRateSpectrum(self, num):

		SPISelect(num)
		tempDict = {1:20, 2:23, 3:24, 4:18, 5:12, 6:19, 7:13}
		GPIOnum = tempDict[num]
		self.updateProgBar(0)
		SRData = []
		AVGData = 0
		for i in range(128):
			self.updateProgBar(i)
			#spi.writebytes(i)
			AVGData = 0
			for j in range(10):
				# Turn on the output
				GPIO.output(GPIOnum, 1)
				# Micro chip automatically measures the data
				time.sleep(0.0001)
				self.I2CLock.acquire()
				try:
					adcReading = bus.read_i2c_block_data(80, 0, 2)
				except:
					self.I2C_ERROR()
					adcReading = bus.read_i2c_block_data(80, 0, 2)
				self.I2CLock.release()
				GPIO.output(GPIOnum, 0)
				readingValue = adcReading[1]
				readingValue += adcReading[0] << 8
				AVGData += readingValue/10
			SRData.append(0.001*float(math.trunc(AVGData*0.00305*1000)))
		return SRData

	#outputs software pwm signals on raspberry pi when the button is pressed
	def btnOut(self, num):
		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']
		buttons = progData[pos]['buttons']
		s.close()

		#get frequency and duty cycle values
		try:
			dc = float(buttons[num]['dc'])
			frq = float(buttons[num]['frq'])
		except:
			dc = frq = ""

		if self.btnList[num].state == "down":
			self.startFunction(num, buttons[num])
		elif self.btnList[num].state == "normal":
			self.stopFunction(num)

	# Given the button object and the button number this starts a signal on the proper GPIO
	# pin with the correct duty cycle and frequency
	def startFunction(self, BtnNum, Button):
		tempDict = {3:18, 4:12, 5:19, 6:13}
		if Button['func'] == 'DC':
			if (BtnNum == 0):
				p0.ChangeDutyCycle(100)
			elif (BtnNum == 1):
				p1.ChangeDutyCycle(100)
			elif (BtnNum == 2):
				p2.ChangeDutyCycle(100)
			else:
				hardPWM.hardware_PWM(tempDict[BtnNum], 1, 1000000)
		else:
			if (BtnNum == 0):
				p0.ChangeFrequency(float(Button['freq']))
				p0.ChangeDutyCycle(float(Button['dc']))
			elif (BtnNum == 1):
				p1.ChangeFrequency(float(Button['freq)']))
				p1.ChangeDutyCycle(float(Button['dc']))
			elif (BtnNum == 2):
				p2.ChangeFrequency(float(Button['freq)']))
				p2.ChangeDutyCycle(float(Button['dc']))
			else:
				hardPWM.hardware_PWM(tempDict[BtnNum], int(Button['freq']), 10000 * int(Button['dc']))

	# Given the button number this function turns off the signal on the corresponding GPIO pin
	def stopFunction(self, BtnNum):
		tempDict = {0:20, 1:23, 2:24, 3:18, 4:12, 5:19, 6:13}
		GPIO.output(tempDict[BtnNum], 0)

class NewProgScreen(Screen):
	#Upon pressing Next, commits the new program title at a new key in the dict
	#Also initializes the dict
	#Dict Structure is documented in OneNote under User Interface Design
	def commitNewProgTitle(self):
		s = shelve.open('TestBoxData.db')

		globalData = s['global']
		progData = s['data']

		pos = globalData['maxpos']
		pos += 1

		progData[pos] = {'title':self.ids.entry.text, 'buttons':{0:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5},1:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5},2:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5},3:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5},4:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5},5:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5},6:{'title':'0','func':'DC','frq':100,'dc':101, 'MaxCurrent':5}}}
		globalData['pos'] = pos
		globalData['maxpos'] = pos
		s['global'] = globalData
		s['data'] = progData
		s.close()

	def updateText(self):
		self.ids.entry.text = ''
		return ''

class EditProgScreen(Screen):

	def updatePWMtxt0(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC0.state == "down")
		self.ids.frqtxt0.disabled = state
		self.ids.dctxt0.disabled = state
		if state:
			self.ids.frqtxt0.background_color = [1,1,1,1]
			self.ids.dctxt0.background_color = [1,1,1,1]

	def updatePWMtxt1(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC1.state == "down")
		self.ids.frqtxt1.disabled = state
		self.ids.dctxt1.disabled = state
		if state:
			self.ids.frqtxt1.background_color = [1,1,1,1]
			self.ids.dctxt1.background_color = [1,1,1,1]

	def updatePWMtxt2(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC2.state == "down")
		self.ids.frqtxt2.disabled = state
		self.ids.dctxt2.disabled = state
		if state:
			self.ids.frqtxt2.background_color = [1,1,1,1]
			self.ids.dctxt2.background_color = [1,1,1,1]

	def updatePWMtxt3(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC3.state == "down")
		self.ids.frqtxt3.disabled = state
		self.ids.dctxt3.disabled = state
		if state:
			self.ids.frqtxt3.background_color = [1,1,1,1]
			self.ids.dctxt3.background_color = [1,1,1,1]

	def updatePWMtxt4(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC4.state == "down")
		self.ids.frqtxt4.disabled = state
		self.ids.dctxt4.disabled = state
		if state:
			self.ids.frqtxt4.background_color = [1,1,1,1]
			self.ids.dctxt4.background_color = [1,1,1,1]

	def updatePWMtxt5(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC5.state == "down")
		self.ids.frqtxt5.disabled = state
		self.ids.dctxt5.disabled = state
		if state:
			self.ids.frqtxt5.background_color = [1,1,1,1]
			self.ids.dctxt5.background_color = [1,1,1,1]

	def updatePWMtxt6(self): #disable text inputs if the DC option is chosen in drop down menu
		state = (self.ids.checkDC6.state == "down")
		self.ids.frqtxt6.disabled = state
		self.ids.dctxt6.disabled = state
		if state:
			self.ids.frqtxt6.background_color = [1,1,1,1]
			self.ids.dctxt6.background_color = [1,1,1,1]

	#put all the info entered into the textinputs into the dictionary and store in in the shelve database
	def commitButtonInfo(self):
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		progData[pos]['buttons'][0]['title'] = self.ids.btntxt0.text
		progData[pos]['buttons'][1]['title'] = self.ids.btntxt1.text
		progData[pos]['buttons'][2]['title'] = self.ids.btntxt2.text
		progData[pos]['buttons'][3]['title'] = self.ids.btntxt3.text
		progData[pos]['buttons'][4]['title'] = self.ids.btntxt4.text
		progData[pos]['buttons'][5]['title'] = self.ids.btntxt5.text
		progData[pos]['buttons'][6]['title'] = self.ids.btntxt6.text

		if self.ids.checkDC0.state == "down":
			progData[pos]['buttons'][0]['func'] = "DC"
		else:
			progData[pos]['buttons'][0]['func'] = "PWM"

		if self.ids.checkDC1.state == "down":
			progData[pos]['buttons'][1]['func'] = "DC"
		else:
			progData[pos]['buttons'][1]['func'] = "PWM"

		if self.ids.checkDC2.state == "down":
			progData[pos]['buttons'][2]['func'] = "DC"
		else:
			progData[pos]['buttons'][2]['func'] = "PWM"

		if self.ids.checkDC3.state == "down":
			progData[pos]['buttons'][3]['func'] = "DC"
		else:
			progData[pos]['buttons'][3]['func'] = "PWM"

		if self.ids.checkDC4.state == "down":
			progData[pos]['buttons'][4]['func'] = "DC"
		else:
			progData[pos]['buttons'][4]['func'] = "PWM"

		if self.ids.checkDC5.state == "down":
			progData[pos]['buttons'][5]['func'] = "DC"
		else:
			progData[pos]['buttons'][5]['func'] = "PWM"

		if self.ids.checkDC6.state == "down":
			progData[pos]['buttons'][6]['func'] = "DC"
		else:
			progData[pos]['buttons'][6]['func'] = "PWM"

		progData[pos]['buttons'][0]['frq'] = self.ids.frqtxt0.text
		progData[pos]['buttons'][1]['frq'] = self.ids.frqtxt1.text
		progData[pos]['buttons'][2]['frq'] = self.ids.frqtxt2.text
		progData[pos]['buttons'][3]['frq'] = self.ids.frqtxt3.text
		progData[pos]['buttons'][4]['frq'] = self.ids.frqtxt4.text
		progData[pos]['buttons'][5]['frq'] = self.ids.frqtxt5.text
		progData[pos]['buttons'][6]['frq'] = self.ids.frqtxt6.text

		progData[pos]['buttons'][0]['dc'] = self.ids.dctxt0.text
		progData[pos]['buttons'][1]['dc'] = self.ids.dctxt1.text
		progData[pos]['buttons'][2]['dc'] = self.ids.dctxt2.text
		progData[pos]['buttons'][3]['dc'] = self.ids.dctxt3.text
		progData[pos]['buttons'][4]['dc'] = self.ids.dctxt4.text
		progData[pos]['buttons'][5]['dc'] = self.ids.dctxt5.text
		progData[pos]['buttons'][6]['dc'] = self.ids.dctxt6.text
		s['data'] = progData
		s.close()

	#resets the data/state of all the text inputs and buttons so old data is not displayed on them
	def updateWidgets(self):
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		pos = globalData['pos']

		progData = s['data']

		self.ids.btntxt0.text = progData[pos]['buttons'][0]['title']
		self.ids.btntxt1.text = progData[pos]['buttons'][1]['title']
		self.ids.btntxt2.text = progData[pos]['buttons'][2]['title']
		self.ids.btntxt3.text = progData[pos]['buttons'][3]['title']
		self.ids.btntxt4.text = progData[pos]['buttons'][4]['title']
		self.ids.btntxt5.text = progData[pos]['buttons'][5]['title']
		self.ids.btntxt6.text = progData[pos]['buttons'][6]['title']

		self.ids.frqtxt0.text = str(progData[pos]['buttons'][0]['frq'])
		self.ids.frqtxt1.text = str(progData[pos]['buttons'][1]['frq'])
		self.ids.frqtxt2.text = str(progData[pos]['buttons'][2]['frq'])
		self.ids.frqtxt3.text = str(progData[pos]['buttons'][3]['frq'])
		self.ids.frqtxt4.text = str(progData[pos]['buttons'][4]['frq'])
		self.ids.frqtxt5.text = str(progData[pos]['buttons'][5]['frq'])
		self.ids.frqtxt6.text = str(progData[pos]['buttons'][6]['frq'])

		self.ids.dctxt0.text = str(progData[pos]['buttons'][0]['dc'])
		self.ids.dctxt1.text = str(progData[pos]['buttons'][1]['dc'])
		self.ids.dctxt2.text = str(progData[pos]['buttons'][2]['dc'])
		self.ids.dctxt3.text = str(progData[pos]['buttons'][3]['dc'])
		self.ids.dctxt4.text = str(progData[pos]['buttons'][4]['dc'])
		self.ids.dctxt5.text = str(progData[pos]['buttons'][5]['dc'])
		self.ids.dctxt6.text = str(progData[pos]['buttons'][6]['dc'])

		state = (progData[pos]['buttons'][0]['func'] == "DC")
		self.ids.frqtxt0.disabled = state
		self.ids.dctxt0.disabled = state
		self.ids.checkDC0.active = state
		self.ids.checkPWM0.active = not(state)

		state = (progData[pos]['buttons'][1]['func'] == "DC")
		self.ids.frqtxt1.disabled = state
		self.ids.dctxt1.disabled = state
		self.ids.checkDC1.active = state
		self.ids.checkPWM1.active = not(state)

		state = (progData[pos]['buttons'][2]['func'] == "DC")
		self.ids.frqtxt2.disabled = state
		self.ids.dctxt2.disabled = state
		self.ids.checkDC2.active = state
		self.ids.checkPWM2.active = not(state)

		state = (progData[pos]['buttons'][3]['func'] == "DC")
		self.ids.frqtxt3.disabled = state
		self.ids.dctxt3.disabled = state
		self.ids.checkDC3.active = state
		self.ids.checkPWM3.active = not(state)

		state = (progData[pos]['buttons'][4]['func'] == "DC")
		self.ids.frqtxt4.disabled = state
		self.ids.dctxt4.disabled = state
		self.ids.checkDC4.active = state
		self.ids.checkPWM4.active = not(state)

		state = (progData[pos]['buttons'][5]['func'] == "DC")
		self.ids.frqtxt5.disabled = state
		self.ids.dctxt5.disabled = state
		self.ids.checkDC5.active = state
		self.ids.checkPWM5.active = not(state)

		state = (progData[pos]['buttons'][6]['func'] == "DC")
		self.ids.frqtxt6.disabled = state
		self.ids.dctxt6.disabled = state
		self.ids.checkDC6.active = state
		self.ids.checkPWM6.active = not(state)

		self.ids.frqtxt0.background_color = [1,1,1,1]
		self.ids.frqtxt1.background_color = [1,1,1,1]
		self.ids.frqtxt2.background_color = [1,1,1,1]
		self.ids.frqtxt3.background_color = [1,1,1,1]
		self.ids.frqtxt4.background_color = [1,1,1,1]
		self.ids.frqtxt5.background_color = [1,1,1,1]
		self.ids.frqtxt6.background_color = [1,1,1,1]

		self.ids.dctxt0.background_color = [1,1,1,1]
		self.ids.dctxt1.background_color = [1,1,1,1]
		self.ids.dctxt2.background_color = [1,1,1,1]
		self.ids.dctxt3.background_color = [1,1,1,1]
		self.ids.dctxt4.background_color = [1,1,1,1]
		self.ids.dctxt5.background_color = [1,1,1,1]
		self.ids.dctxt6.background_color = [1,1,1,1]

	def checkValidInfo(self):
		'''
		frqtxt0-6 and dctxt0-6 are boolean variables that are set to True if
		the corresponding text inputs are valid, otherwise they are set false
		'''
		frqtxt0 = frqtxt1 = frqtxt2 = frqtxt3 = frqtxt4 = frqtxt5 = frqtxt6 = dctxt0 = dctxt1 = dctxt2 = dctxt3 = dctxt4 = dctxt5 = dctxt6 = True

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC0.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if float(self.ids.frqtxt0.text) > 0:
					frqtxt0 = True
					self.ids.frqtxt0.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt0 = False
					self.ids.frqtxt0.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt0 = False
				self.ids.frqtxt0.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt0.text) <= 100:
					dctxt0 = True
					self.ids.dctxt0.background_color = [1,1,1,1]
				else:
					dctxt0 = False
					self.ids.dctxt0.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt0 = False
				self.ids.dctxt0.background_color = [1,.15,0,1]
				self.popup.open()

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC1.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if float(self.ids.frqtxt1.text) > 0:
					frqtxt1 = True
					self.ids.frqtxt1.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt1 = False
					self.ids.frqtxt1.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt1 = False
				self.ids.frqtxt1.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt1.text) <= 100:
					dctxt1 = True
					self.ids.dctxt1.background_color = [1,1,1,1]
				else:
					dctxt1 = False
					self.ids.dctxt1.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt1 = False
				self.ids.dctxt1.background_color = [1,.15,0,1]
				self.popup.open()

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC2.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if float(self.ids.frqtxt2.text) > 0:
					frqtxt2 = True
					self.ids.frqtxt2.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt2 = False
					self.ids.frqtxt2.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt2 = False
				self.ids.frqtxt2.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt2.text) <= 100:
					dctxt2 = True
					self.ids.dctxt2.background_color = [1,1,1,1]
				else:
					dctxt2 = False
					self.ids.dctxt2.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt2 = False
				self.ids.dctxt2.background_color = [1,.15,0,1]
				self.popup.open()

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC3.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if float(self.ids.frqtxt3.text) > 0:
					frqtxt3 = True
					self.ids.frqtxt3.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt3 = False
					self.ids.frqtxt3.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt3 = False
				self.ids.frqtxt3.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt3.text) <= 100:
					dctxt3 = True
					self.ids.dctxt3.background_color = [1,1,1,1]
				else:
					dctxt3 = False
					self.ids.dctxt3.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt3 = False
				self.ids.dctxt3.background_color = [1,.15,0,1]
				self.popup.open()

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC4.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if float(self.ids.frqtxt4.text) > 0:
					frqtxt4 = True
					self.ids.frqtxt4.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt4 = False
					self.ids.frqtxt4.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt4 = False
				self.ids.frqtxt4.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt4.text) <= 100:
					dctxt4 = True
					self.ids.dctxt4.background_color = [1,1,1,1]
				else:
					dctxt4 = False
					self.ids.dctxt4.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt4 = False
				self.ids.dctxt4.background_color = [1,.15,0,1]
				self.popup.open()

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC5.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if int(self.ids.frqtxt5.text) > 0:
					frqtxt5 = True
					self.ids.frqtxt5.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt5 = False
					self.ids.frqtxt5.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt5 = False
				self.ids.frqtxt5.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt5.text) <= 100:
					dctxt5 = True
					self.ids.dctxt5.background_color = [1,1,1,1]
				else:
					dctxt5 = False
					self.ids.dctxt5.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt5 = False
				self.ids.dctxt5.background_color = [1,.15,0,1]
				self.popup.open()

		#if channel is selected to be DC, then the text inputs are disabled and there is no need to check if the text inputs are valid
		if self.ids.checkDC6.active == False:

			#try to convert text input to base 10 number, if it works the isnput is a valid integer
			try:
				#frequency input is valid if it is an integer greater than 0
				if int(self.ids.frqtxt6.text) > 0:
					frqtxt6 = True
					self.ids.frqtxt6.background_color = [1,1,1,1]
				#if it is less than 0, make the text input red and open the popup window
				else:
					frqtxt6 = False
					self.ids.frqtxt6.background_color = [1,.15,0,1]
					self.popup.open()

			#if a ValueError is thrown, the text input was not a valid integer
			except ValueError:
				frqtxt6 = False
				self.ids.frqtxt6.background_color = [1,.15,0,1]
				self.popup.open()

			#duty cycle input is valid if it is an integer between 0-100T
			try:
				if 0 < int(self.ids.dctxt6.text) <= 100:
					dctxt6 = True
					self.ids.dctxt6.background_color = [1,1,1,1]
				else:
					dctxt6 = False
					self.ids.dctxt6.background_color = [1,.15,0,1]
					self.popup.open()
			except ValueError:
				dctxt6 = False
				self.ids.dctxt6.background_color = [1,.15,0,1]
				self.popup.open()


		if frqtxt0 and frqtxt1 and frqtxt2 and frqtxt3 and frqtxt4 and frqtxt5 and frqtxt6 and dctxt0 and dctxt1 and dctxt2 and dctxt3 and dctxt4 and dctxt5 and dctxt6:
			return "home"
		else:
			return "editprog"

class ScreenManagement(ScreenManager):
	def __init__(self, **kwargs):
		ScreenManager.__init__(self, **kwargs)


class MainApp(App):
	pass

if __name__ == "__main__":
	MainApp().run()
