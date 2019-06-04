from kivy.app import App
#kivy.require("1.8.0")
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Line
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.uix.togglebutton import ToggleButton
from GPIO_Timer import GPIO_Timer
import shelve
import pigpio
import atexit
import RPi.GPIO as GPIO
import spidev
import CurrentSensor

#------------------------------------------------------------------------------#
#                                                                              #
#     Code structure is documented in OneNote under User Interface Design      #
#                                                                              #
#------------------------------------------------------------------------------#

#reset GPIO pin functions at exit of program
atexit.register(GPIO.cleanup)

#set GPIO to BCM numbering scheme. Pin numbering can be found at pinout.xyz
GPIO.setmode(GPIO.BCM)

#initialize software pwm
#btn0
GPIO.setup(17, GPIO.OUT)
p0 = GPIO.PWM(17, 1)
p0.start(0)

#btn1
GPIO.setup(27, GPIO.OUT)
p1 = GPIO.PWM(27, 1)
p1.start(0)

#btn2
GPIO.setup(22, GPIO.OUT)
p2 = GPIO.PWM(22, 1)
p2.start(0)

#btn3
GPIO.setup(23, GPIO.OUT)
p3 = GPIO.PWM(23, 1)
p3.start(0)

#btn4
GPIO.setup(24, GPIO.OUT)
p4 = GPIO.PWM(24, 1)
p4.start(0)

#initialize hardware PWM
hardPWM = pigpio.pi()

#initialize GPIO callack timer to test timing of voltage events on pins
myTimer = GPIO_Timer(5,6)
myTimer.startCallBack()

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
		
		s = shelf.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		s.close()

		buttonData = progData[globalData['pos']]['buttons']
		self.currentSensor = CurrentSensor(buttonData)

	#this updates the buttons upon entering the screen to reflect their current state
	def updateScreen(self):
		s = shelve.open('TestBoxData.db')

		# Get a temporary copy of the global data dictionary stored in the shelve database
		globalData = s['global']

		# Get a temporary copy of the program data dictionary in the shelve database
		progData = s['data']

		#globalData['pos'] is the current program variable
		pos = globalData['pos']

		#update buttons
		self.ids.btn0.text = str(progData[pos]['buttons'][0]['title'])
		self.ids.btn1.text = str(progData[pos]['buttons'][1]['title'])
		self.ids.btn2.text = str(progData[pos]['buttons'][2]['title'])
		self.ids.btn3.text = str(progData[pos]['buttons'][3]['title'])
		self.ids.btn4.text = str(progData[pos]['buttons'][4]['title'])
		self.ids.btn5.text = str(progData[pos]['buttons'][5]['title'])
		self.ids.btn6.text = str(progData[pos]['buttons'][6]['title'])
		self.ids.btn0.state = "normal"
		self.ids.btn1.state = "normal"
		self.ids.btn2.state = "normal"
		self.ids.btn3.state = "normal"
		self.ids.btn4.state = "normal"
		self.ids.btn5.state = "normal"
		self.ids.btn6.state = "normal"

		#update screen title
		self.ids.switchtitle.text = str(progData[pos]['title'])

		#update button property labels
		self.ids.btn0func.text = str(progData[pos]['buttons'][0]['func'])
		if progData[pos]['buttons'][0]['func'] == 'PWM':
			self.ids.btn0frq.text = str(progData[pos]['buttons'][0]['frq']) + ' Hz'
			self.ids.btn0dc.text = str(progData[pos]['buttons'][0]['dc']) + "% dc"
		else:
			self.ids.btn0frq.text = ""
			self.ids.btn0dc.text = ""

		self.ids.btn1func.text = str(progData[pos]['buttons'][1]['func'])
		if progData[pos]['buttons'][1]['func'] == 'PWM':
			self.ids.btn1frq.text = str(progData[pos]['buttons'][1]['frq']) + ' Hz'
			self.ids.btn1dc.text = str(progData[pos]['buttons'][1]['dc']) + "% dc"
		else:
			self.ids.btn1frq.text = ""
			self.ids.btn1dc.text = ""

		self.ids.btn2func.text = str(progData[pos]['buttons'][2]['func'])
		if progData[pos]['buttons'][2]['func'] == 'PWM':
			self.ids.btn2frq.text = str(progData[pos]['buttons'][2]['frq']) + ' Hz'
			self.ids.btn2dc.text = str(progData[pos]['buttons'][2]['dc']) + "% dc"
		else:
			self.ids.btn2frq.text = ""
			self.ids.btn2dc.text = ""

		self.ids.btn3func.text = str(progData[pos]['buttons'][3]['func'])
		if progData[pos]['buttons'][3]['func'] == 'PWM':
			self.ids.btn3frq.text = str(progData[pos]['buttons'][3]['frq']) + ' Hz'
			self.ids.btn3dc.text = str(progData[pos]['buttons'][3]['dc']) + "% dc"
		else:
			self.ids.btn3frq.text = ""
			self.ids.btn3dc.text = ""

		self.ids.btn4func.text = str(progData[pos]['buttons'][4]['func'])
		if progData[pos]['buttons'][4]['func'] == 'PWM':
			self.ids.btn4frq.text = str(progData[pos]['buttons'][4]['frq']) + ' Hz'
			self.ids.btn4dc.text = str(progData[pos]['buttons'][4]['dc']) + "% dc"
		else:
			self.ids.btn4frq.text = ""
			self.ids.btn4dc.text = ""

		self.ids.btn5func.text = str(progData[pos]['buttons'][5]['func'])
		if progData[pos]['buttons'][5]['func'] == 'PWM':
			self.ids.btn5frq.text = str(progData[pos]['buttons'][5]['frq']) + ' Hz'
			self.ids.btn5dc.text = str(progData[pos]['buttons'][5]['dc']) + "% dc"
		else:
			self.ids.btn5frq.text = ""
			self.ids.btn5dc.text = ""

		self.ids.btn6func.text = str(progData[pos]['buttons'][6]['func'])
		if progData[pos]['buttons'][6]['func'] == 'PWM':
			self.ids.btn6frq.text = str(progData[pos]['buttons'][6]['frq']) + ' Hz'
			self.ids.btn6dc.text = str(progData[pos]['buttons'][6]['dc']) + "% dc"
		else:
			self.ids.btn6frq.text = ""
			self.ids.btn6dc.text = ""

		self.ids.togbtn0.state = "normal"
		self.ids.togbtn1.state = "normal"
		self.ids.togbtn2.state = "normal"
		self.ids.togbtn3.state = "normal"
		self.ids.togbtn4.state = "normal"
		self.ids.togbtn5.state = "normal"
		self.ids.togbtn6.state = "normal"

		s.close()

	# Called when the back button is pressed
	# Stops PWM outputs on leaving the switch screen and makes sure that all current sensor
	# threads are joined/killed
	def stopPWM(self):
		p0.ChangeDutyCycle(0)
		p1.ChangeDutyCycle(0)
		p2.ChangeDutyCycle(0)
		p3.ChangeDutyCycle(0)
		p4.ChangeDutyCycle(0)
		hardPWM.hardware_PWM(18,1,0)
		hardPWM.hardware_PWM(19,1,0)
		if self.ids.btn0.state == "down":
			try:
				self.currentSensor.stopRead(0)
			except Exception as e:
				raise e
		elif self.ids.btn1.state == "down":
			try:
				self.currentSensor.stopRead(1)
			except Exception as e:
				raise e
		elif self.ids.btn2.state == "down":
			try:
				self.currentSensor.stopRead(2)
			except Exception as e:
				raise e
		elif self.ids.btn3.state == "down":
			try:
				self.currentSensor.stopRead(3)
			except Exception as e:
				raise e
		elif self.ids.btn4.state == "down":
			try:
				self.currentSensor.stopRead(4)
			except Exception as e:
				raise e
		elif self.ids.btn5.state == "down":
			try:
				self.currentSensor.stopRead(5)
			except Exception as e:
				raise e
		elif self.ids.btn6.state == "down":
			try:
				self.currentSensor.stopRead(6)
			except Exception as e:
				raise e

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

	#determine and display slew rate on selected channel
	def testSlewRate(self):
		if self.ids.togbtn0.state == "down":
			p0.ChangeDutyCycle(100)
			while True:
				if GPIO.input(17) == 1:
					p0.ChangeDutyCycle(0)
					break
		elif self.ids.togbtn1.state == "down":
			p1.ChangeDutyCycle(100)
			while True:
				if GPIO.input(27) == 1:
					p1.ChangeDutyCycle(0)
					break
		elif self.ids.togbtn2.state == "down":
			p2.ChangeDutyCycle(100)
			while True:
				if GPIO.input(22) == 1:
					p2.ChangeDutyCycle(0)
					break
		elif self.ids.togbtn3.state == "down":
			p3.ChangeDutyCycle(100)
			while True:
				if GPIO.input(23) == 1:
					p3.ChangeDutyCycle(0)
					break
		elif self.ids.togbtn4.state == "down":
			p4.ChangeDutyCycle(100)
			while True:
				if GPIO.input(24) == 1:
					p4.ChangeDutyCycle(0)
					break
		elif self.ids.togbtn5.state == "down":
			hardPWM.hardware_PWM(18,1,1000000)
			while True:
				if hardPWM.read(18) == 1:
					hardPWM.hardware_PWM(18,1,0)
					break
		elif self.ids.togbtn6.state == "down":
			hardPWM.hardware_PWM(19,1,1000000)
			while True:
				if hardPWM.read(19) == 1:
					hardPWM.hardware_PWM(19,1,0)
					break
		myTime = myTimer.getElapsedTime()
		if myTime > 0:
			mySlewRate = "{0:.2f}".format((10.5-2.5)/myTime)
		else:
			mySlewRate = "Error"
		self.ids.popslewdisplay.text = "Slew Rate: {}, V/us ".format(mySlewRate)

	#outputs software pwm signals on raspberry pi when the button is pressed
	def btn0Out(self):
		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = float(progData[pos]['buttons'][0]['dc'])
			frq = float(progData[pos]['buttons'][0]['frq'])
		except:
			dc = frq = ""

		# Here we start the current listener

		if progData[pos]['buttons'][0]['func'] == 'DC':
			if self.ids.btn0.state == "down":
					self.currentSensor.startRead(0)
					p0.ChangeDutyCycle(100)
			elif self.ids.btn0.state == "normal":
					p0.ChangeDutyCycle(0)
					self.currentSensor.stopRead(0)
		if progData[pos]['buttons'][0]['func'] == 'PWM':
			try:
				p0.ChangeFrequency(frq)
				if self.ids.btn0.state == "down":
						self.currentSensor.startRead(0)
						p0.ChangeDutyCycle(dc)
				elif self.ids.btn0.state == "normal":
						p0.ChangeDutyCycle(0)
						self.currentSensor.stopRead(0)
			except:
				pass
		s.close()

	#outputs software pwm signals on raspberry pi when the button is pressed
	def btn1Out(self):

		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = float(progData[pos]['buttons'][1]['dc'])
			frq = float(progData[pos]['buttons'][1]['frq'])
		except:
			dc = frq = ""

		if progData[pos]['buttons'][1]['func'] == 'DC':
			if self.ids.btn1.state == "down":
				self.currentSensor.startRead(1)
				p1.ChangeDutyCycle(100)
			elif self.ids.btn1.state == "normal":
				p1.ChangeDutyCycle(0)
				self.currentSensor.stopRead(1)
		if progData[pos]['buttons'][1]['func'] == 'PWM':
			try:
				p1.ChangeFrequency(frq)
				if self.ids.btn1.state == "down":
					self.currentSensor.startRead(1)
					p1.ChangeDutyCycle(dc)
				elif self.ids.btn1.state == "normal":
					p1.ChangeDutyCycle(0)
					self.currentSensor.stopRead(1)
			except:
				pass
		s.close()

	#outputssoftware  pwm signals on raspberry pi when the button is pressed
	def btn2Out(self):

		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = float(progData[pos]['buttons'][2]['dc'])
			frq = float(progData[pos]['buttons'][2]['frq'])
		except:
			dc = frq = ""

		if progData[pos]['buttons'][2]['func'] == 'DC':
			if self.ids.btn2.state == "down":
				self.currentSensor.startRead(2)
				p2.ChangeDutyCycle(100)
			elif self.ids.btn2.state == "normal":
				p2.ChangeDutyCycle(0)
				self.currentSensor.stopRead(2)
		if progData[pos]['buttons'][2]['func'] == 'PWM':
			try:
				p2.ChangeFrequency(frq)
				if self.ids.btn2.state == "down":
					self.currentSensor.startRead(2)
					p2.ChangeDutyCycle(dc)
				elif self.ids.btn2.state == "normal":
					p2.ChangeDutyCycle(0)
					self.currentSensor.stopRead(2)
			except:
				pass
		s.close()

	#outputs software pwm signals on raspberry pi when the button is pressed
	def btn3Out(self):

		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = float(progData[pos]['buttons'][3]['dc'])
			frq = float(progData[pos]['buttons'][3]['frq'])
		except:
			dc = frq = ""

		if progData[pos]['buttons'][3]['func'] == 'DC':
			if self.ids.btn3.state == "down":
				self.currentSensor.startRead(3)
				p3.ChangeDutyCycle(100)
			elif self.ids.btn3.state == "normal":
				p3.ChangeDutyCycle(0)
				self.currentSensor.stopRead(3)
		if temp[pos]['buttons'][3]['func'] == 'PWM':
			try:
				p3.ChangeFrequency(frq)
				if self.ids.btn3.state == "down":
					self.currentSensor.startRead(3)
					p3.ChangeDutyCycle(dc)
				elif self.ids.btn3.state == "normal":
					p3.ChangeDutyCycle(0)
					self.currentSensor.stopRead(3)
			except:
				pass
		s.close()

	#outputs software pwm signals on raspberry pi when the button is pressed
	def btn4Out(self):

		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = float(progData[pos]['buttons'][4]['dc'])
			frq = float(progData[pos]['buttons'][4]['frq'])
		except:
			dc = frq = ""

		if progData[pos]['buttons'][4]['func'] == 'DC':
			if self.ids.btn4.state == "down":
				self.currentSensor.startRead(4)
				p4.ChangeDutyCycle(100)
			elif self.ids.btn4.state == "normal":
				p4.ChangeDutyCycle(0)
				self.currentSensor.startRead(4)
		if progData[pos]['buttons'][4]['func'] == 'PWM':
			try:
				p4.ChangeFrequency(frq)
				if self.ids.btn4.state == "down":
					self.currentSensor.startRead(4)
					p4.ChangeDutyCycle(dc)
				elif self.ids.btn4.state == "normal":
					p4.ChangeDutyCycle(0)
					self.currentSensor.startRead(4)
			except:
				pass

		s.close()

	#outputs hardware pwm signals on raspberry pi when the button is pressed
	def btn5Out(self):
		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = 10000 * int(progData[pos]['buttons'][5]['dc'])
			frq = int(progData[pos]['buttons'][5]['frq'])
		except:
			dc = frq = ""

		if progData[pos]['buttons'][5]['func'] == 'DC':
			if self.ids.btn5.state == "down":
				self.currentSensor.startRead(5)
				hardPWM.hardware_PWM(18,1,1000000)
			elif self.ids.btn5.state == "normal":
				hardPWM.hardware_PWM(18,1,0)
				self.currentSensor.startRead(5)
		if progData[pos]['buttons'][5]['func'] == 'PWM':
			try:
				if self.ids.btn5.state == "down":
					self.currentSensor.startRead(5)
					hardPWM.hardware_PWM(18,frq,dc)
				elif self.ids.btn5.state == "normal":
					hardPWM.hardware_PWM(18,1,0)
					self.currentSensor.startRead(5)
			except Exception as e:
				raise e
		s.close()

	#outputs hardware signals on raspberry pi when the button is pressed
	def btn6Out(self):
		#open database and save copy to temporary dictionary
		s = shelve.open('TestBoxData.db')
		globalData = s['global']
		progData = s['data']
		pos = globalData['pos']

		#get frequency and duty cycle values
		try:
			dc = 10000 * int(progData[pos]['buttons'][6]['dc'])
			frq = int(progData[pos]['buttons'][6]['frq'])
		except:
			dc = frq = ""

		if progData[pos]['buttons'][6]['func'] == 'DC':
			if self.ids.btn6.state == "down":
				self.currentSensor.startRead(6)
				hardPWM.hardware_PWM(19,1,1000000)
			elif self.ids.btn6.state == "normal":
				hardPWM.hardware_PWM(19,1,0)
				self.currentSensor.startRead(6)
		if progData[pos]['buttons'][6]['func'] == 'PWM':
			try:
				if self.ids.btn6.state == "down":
					self.currentSensor.startRead(6)
					hardPWM.hardware_PWM(19,frq,dc)
				elif self.ids.btn6.state == "normal":
					hardPWM.hardware_PWM(19,1,0)
					self.currentSensor.startRead(6)
			except Exception as e:
				raise e	
		s.close()

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
		
		progData[pos] = {'title':self.ids.entry.text, 'buttons':{0:{'title':'0','func':'DC','frq':100,'dc':101},1:{'title':'0','func':'DC','frq':100,'dc':101},2:{'title':'0','func':'DC','frq':100,'dc':101},3:{'title':'0','func':'DC','frq':100,'dc':101},4:{'title':'0','func':'DC','frq':100,'dc':101},5:{'title':'0','func':'DC','frq':100,'dc':101},6:{'title':'0','func':'DC','frq':100,'dc':101}}}
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
