from kivy.app import App
#kivy.require("1.8.0")
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import Line
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.uix.togglebutton import ToggleButton
from GPIO_Timer import GPIO_Timer
import shelve
import pigpio
import atexit
import RPi.GPIO as GPIO
import spidev

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
hardPWM0 = pigpio.pi()

#initialize GPIO callack timer to test timing of voltage events on pins
myTimer = GPIO_Timer(5,6)
myTimer.startCallBack()

#initialize SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000000

class HomeScreen(Screen):
    #sets the value at the 'del' position in the dict to a value that represents either the choose program, delete program, or edit program function
    #param: func: the value (either 0,1,2) that temp['del'] will be set to
    def setFunc(self, func):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']
        temp['del'] = func
        s['key1'] = temp
        s.close()

class ChooseProgScreen(Screen):
     #There are 24 buttons for potential programs to be added
     #The buttons pop up in the ChooseProgScreen when a new program has been added
     #This is a hacky way to do it. There is a better way to do it adding buttons in the python code. There is an example of how to do it in OneNote

    #this updates the buttons and labels upon entering the screen to reflect their current state
    def updateButtons(self):
        s = shelve.open('test1.db')
        temp = s['key1']

        self.ids.lblTitle.text = self.getLblTxt()

        self.ids.btn1.text = self.getBtnTxt(1)
        self.ids.btn1.color = 1,1,1,self.getClr(1)
        self.ids.btn1.background_color = 1,1,1,self.getClr(1)

        self.ids.btn2.text = self.getBtnTxt(2)
        self.ids.btn2.color = 1,1,1,self.getClr(2)
        self.ids.btn2.background_color = 1,1,1,self.getClr(2)

        self.ids.btn3.text = self.getBtnTxt(3)
        self.ids.btn3.color = 1,1,1,self.getClr(3)
        self.ids.btn3.background_color = 1,1,1,self.getClr(3)

        self.ids.btn4.text = self.getBtnTxt(4)
        self.ids.btn4.color = 1,1,1,self.getClr(4)
        self.ids.btn4.background_color = 1,1,1,self.getClr(4)

        self.ids.btn5.text = self.getBtnTxt(5)
        self.ids.btn5.color = 1,1,1,self.getClr(5)
        self.ids.btn5.background_color = 1,1,1,self.getClr(5)

        self.ids.btn6.text = self.getBtnTxt(6)
        self.ids.btn6.color = 1,1,1,self.getClr(6)
        self.ids.btn6.background_color = 1,1,1,self.getClr(6)

        self.ids.btn7.text = self.getBtnTxt(7)
        self.ids.btn7.color = 1,1,1,self.getClr(7)
        self.ids.btn7.background_color = 1,1,1,self.getClr(7)

        self.ids.btn8.text = self.getBtnTxt(8)
        self.ids.btn8.color = 1,1,1,self.getClr(8)
        self.ids.btn8.background_color = 1,1,1,self.getClr(8)

        self.ids.btn9.text = self.getBtnTxt(9)
        self.ids.btn9.color = 1,1,1,self.getClr(9)
        self.ids.btn9.background_color = 1,1,1,self.getClr(9)

        self.ids.btn10.text = self.getBtnTxt(10)
        self.ids.btn10.color = 1,1,1,self.getClr(10)
        self.ids.btn10.background_color = 1,1,1,self.getClr(10)

        self.ids.btn11.text = self.getBtnTxt(11)
        self.ids.btn11.color = 1,1,1,self.getClr(11)
        self.ids.btn11.background_color = 1,1,1,self.getClr(11)

        self.ids.btn12.text = self.getBtnTxt(12)
        self.ids.btn12.color = 1,1,1,self.getClr(12)
        self.ids.btn12.background_color = 1,1,1,self.getClr(12)

        self.ids.btn13.text = self.getBtnTxt(13)
        self.ids.btn13.color = 1,1,1,self.getClr(13)
        self.ids.btn13.background_color = 1,1,1,self.getClr(13)

        self.ids.btn14.text = self.getBtnTxt(14)
        self.ids.btn14.color = 1,1,1,self.getClr(14)
        self.ids.btn14.background_color = 1,1,1,self.getClr(14)

        self.ids.btn15.text = self.getBtnTxt(15)
        self.ids.btn15.color = 1,1,1,self.getClr(15)
        self.ids.btn15.background_color = 1,1,1,self.getClr(15)

        self.ids.btn16.text = self.getBtnTxt(16)
        self.ids.btn16.color = 1,1,1,self.getClr(16)
        self.ids.btn16.background_color = 1,1,1,self.getClr(16)

        self.ids.btn17.text = self.getBtnTxt(17)
        self.ids.btn17.color = 1,1,1,self.getClr(17)
        self.ids.btn17.background_color = 1,1,1,self.getClr(17)

        self.ids.btn18.text = self.getBtnTxt(18)
        self.ids.btn18.color = 1,1,1,self.getClr(18)
        self.ids.btn18.background_color = 1,1,1,self.getClr(18)

        self.ids.btn19.text = self.getBtnTxt(19)
        self.ids.btn19.color = 1,1,1,self.getClr(19)
        self.ids.btn19.background_color = 1,1,1,self.getClr(19)

        self.ids.btn20.text = self.getBtnTxt(20)
        self.ids.btn20.color = 1,1,1,self.getClr(20)
        self.ids.btn20.background_color = 1,1,1,self.getClr(20)

        self.ids.btn21.text = self.getBtnTxt(21)
        self.ids.btn21.color = 1,1,1,self.getClr(21)
        self.ids.btn21.background_color = 1,1,1,self.getClr(21)

        self.ids.btn22.text = self.getBtnTxt(22)
        self.ids.btn22.color = 1,1,1,self.getClr(22)
        self.ids.btn22.background_color = 1,1,1,self.getClr(22)

        self.ids.btn23.text = self.getBtnTxt(23)
        self.ids.btn23.color = 1,1,1,self.getClr(23)
        self.ids.btn23.background_color = 1,1,1,self.getClr(23)

        self.ids.btn24.text = self.getBtnTxt(24)
        self.ids.btn24.color = 1,1,1,self.getClr(24)
        self.ids.btn24.background_color = 1,1,1,self.getClr(24)

        s.close()

    # returns the title of the current program to be the title of the corresponding button
    # parameters: btn: the number of the current button whose title is to be returned
    def getBtnTxt(self, btn):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']
        if btn in temp:
            text = temp[btn]['title']
        else:
            text = "error"
        s.close()
        return text

    #returns the appropriate title based on the number at the 'del' position in the dict
    #returns a title for either the choose program screen, the Edit program screen or the Delete program screen
    def getLblTxt(self):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']

        #check what mode chooseprog screen is in and set 'title' variable based on that
        if temp['del'] == 0:
            title = 'Choose Program'
        elif temp['del'] == 1:
            title = 'Choose Program to Edit'
        elif temp['del'] == 2:
            title = 'Choose Program to Delete'
        s.close()
        return title

    #called in the delete program screen
    #deletes one program's information from the dictionary and shifts the subsequent programs back one position
    def setFunc(self):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']

        #get the number of the current program
        btn = temp['btn']

        #check if the chooseprog screen is in delete mode
        if temp['del'] == 2:
            if btn in temp:

                #delete the current program information and shift all the subsequent programs back one position
                del temp[btn]
                for i in range(btn,25):
                    if i in temp and i > 1:
                        temp[i-1] = temp.pop(i)

                #decrement the current program variable
                temp['pos'] = temp['pos'] -1
                temp['maxpos'] = temp['maxpos'] -1
        s['key1'] = temp
        s.close()

    #called when the buttons in chooseprog screen are pressed
    #only opens popup if chooseprog screen is in delete mode
    def popOpen(self, btn):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']

        #check if chooseprog screen is in delete mode
        if temp['del'] == 2:
            if btn in temp:
                #open popup
                self.popup.open()

        #each button in chooseprog screen calls this function with a different number between 1-24
        #temp['btn'] is set to the number of the button that called this function when it was pressed
        temp['btn'] = btn
        s['key1'] = temp
        s.close()

    #called when buttons in chooseprog screen are pressed
    #returns the name of the screen that will be linked to
    def getScrn(self):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']

        #temp['btn'] is the number of the button in chooseprog screen that called this function
        btn = temp['btn']

        #only update temp['pos'] if it is not on the delete screen
        if not (temp['del'] == 2):
            temp['pos'] = btn

        #there 24 buttons, so btn could be any number from 1-24, but temp only contains the number of programs that have been initialized in the software through the Add New Program button
        #this checks if the button pressed is associated with a valid program in 'temp'
        if btn in temp:

            #check what mode chooseprog screen is currently in and return the name of the appropriate screen to be linked to
            if temp['del'] == 2:
                scrn = 'chooseprog'
            elif temp['del'] == 1:
                scrn = 'newprog1'
            else:
                scrn = 'switch'

        #if btn does not correspond to a valid program in 'temp', then this function returns the name of the current screen, 'chooseprog'
        #this is so that pressing random buttons on the chooseprog screen don't change the current screen
        else:
            scrn = "chooseprog"

        #save the temporary copy of the dictionary back to the shelve dictionary
        s['key1'] = temp
        s.close()
        self.updateButtons()
        return scrn

    # returns an int representing an alpha value
    # the alpha value is an opacity. 1 = visible, 0 = invisible
    # this makes buttons that have programs associated with them visible, and buttons that don't invisible
    # parameters: btn: the number of the current button whose title is to be returned
    def getClr(self, btn):
        s = shelve.open('test1.db')
        temp = s['key1']
        if btn in temp:
            alpha = 1
        else:
            alpha = 0
        s.close()
        return alpha

class SwitchScreen(Screen):

    #this updates the buttons upon entering the screen to reflect their current state
    def updateScreen(self):
        s = shelve.open('test1.db')

        #get a temporary copy of the dictionary stored in the shelve database
        temp = s['key1']

        #temp['pos'] is the current program variable
        pos = temp['pos']

        #update buttons
        self.ids.btn0.text = str(temp[pos]['buttons'][0]['title'])
        self.ids.btn1.text = str(temp[pos]['buttons'][1]['title'])
        self.ids.btn2.text = str(temp[pos]['buttons'][2]['title'])
        self.ids.btn3.text = str(temp[pos]['buttons'][3]['title'])
        self.ids.btn4.text = str(temp[pos]['buttons'][4]['title'])
        self.ids.btn5.text = str(temp[pos]['buttons'][5]['title'])
        self.ids.btn6.text = str(temp[pos]['buttons'][6]['title'])
        self.ids.btn0.state = "normal"
        self.ids.btn1.state = "normal"
        self.ids.btn2.state = "normal"
        self.ids.btn3.state = "normal"
        self.ids.btn4.state = "normal"
        self.ids.btn5.state = "normal"
        self.ids.btn6.state = "normal"

        #update screen title
        self.ids.switchtitle.text = str(temp[pos]['title'])

        #update button property labels
        self.ids.btn0func.text = str(temp[pos]['buttons'][0]['func'])
        if temp[pos]['buttons'][0]['func'] == 'PWM':
            self.ids.btn0frq.text = str(temp[pos]['buttons'][0]['dc']) + ' Hz'
            self.ids.btn0dc.text = str(temp[pos]['buttons'][0]['frq']) + "% dc"
        else:
            self.ids.btn0frq.text = ""
            self.ids.btn0dc.text = ""

        self.ids.btn1func.text = str(temp[pos]['buttons'][1]['func'])
        if temp[pos]['buttons'][1]['func'] == 'PWM':
            self.ids.btn1frq.text = str(temp[pos]['buttons'][1]['dc']) + ' Hz'
            self.ids.btn1dc.text = str(temp[pos]['buttons'][1]['frq']) + "% dc"
        else:
            self.ids.btn1frq.text = ""
            self.ids.btn1dc.text = ""

        self.ids.btn2func.text = str(temp[pos]['buttons'][2]['func'])
        if temp[pos]['buttons'][2]['func'] == 'PWM':
            self.ids.btn2frq.text = str(temp[pos]['buttons'][2]['dc']) + ' Hz'
            self.ids.btn2dc.text = str(temp[pos]['buttons'][2]['frq']) + "% dc"
        else:
            self.ids.btn2frq.text = ""
            self.ids.btn2dc.text = ""

        self.ids.btn3func.text = str(temp[pos]['buttons'][3]['func'])
        if temp[pos]['buttons'][3]['func'] == 'PWM':
            self.ids.btn3frq.text = str(temp[pos]['buttons'][3]['dc']) + ' Hz'
            self.ids.btn3dc.text = str(temp[pos]['buttons'][3]['frq']) + "% dc"
        else:
            self.ids.btn3frq.text = ""
            self.ids.btn3dc.text = ""

        self.ids.btn4func.text = str(temp[pos]['buttons'][4]['func'])
        if temp[pos]['buttons'][4]['func'] == 'PWM':
            self.ids.btn4frq.text = str(temp[pos]['buttons'][4]['dc']) + ' Hz'
            self.ids.btn4dc.text = str(temp[pos]['buttons'][4]['frq']) + "% dc"
        else:
            self.ids.btn4frq.text = ""
            self.ids.btn4dc.text = ""

        self.ids.btn5func.text = str(temp[pos]['buttons'][5]['func'])
        if temp[pos]['buttons'][5]['func'] == 'PWM':
            self.ids.btn5frq.text = str(temp[pos]['buttons'][5]['dc']) + ' Hz'
            self.ids.btn5dc.text = str(temp[pos]['buttons'][5]['frq']) + "% dc"
        else:
            self.ids.btn5frq.text = ""
            self.ids.btn5dc.text = ""

        self.ids.btn6func.text = str(temp[pos]['buttons'][6]['func'])
        if temp[pos]['buttons'][6]['func'] == 'PWM':
            self.ids.btn6frq.text = str(temp[pos]['buttons'][6]['dc']) + ' Hz'
            self.ids.btn6dc.text = str(temp[pos]['buttons'][6]['frq']) + "% dc"
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

    #called when the back button is pressed
    #stops PWM outputs on leaving the switch screen
    def stopPWM(self):
        p0.ChangeDutyCycle(0)
        p1.ChangeDutyCycle(0)
        p2.ChangeDutyCycle(0)
        p3.ChangeDutyCycle(0)
        p4.ChangeDutyCycle(0)
        hardPWM0.hardware_PWM(18,1,0)
        hardPWM0.hardware_PWM(19,1,0)

    #get button dc, frq to display below button
    def getbtnInfo(self,btn):
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['pos']
        if btn in temp:
            dc =str(temp[pos]['buttons'][btn]['dc'])
            frq =str(temp[pos]['buttons'][btn]['frq'])
        else:
            dc = frq = ""
        btnInfo = [frq,dc]
        s.close()
        return btnInfo

    #send new value to potentiometer via SPI bus
    def updatePot(self):
        intVal = int(self.ids.slide.value)
        spi.xfer([0x00, intVal])

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
            hardPWM0.hardware_PWM(18,1,1000000)
            while True:
                if hardPWM0.read(18) == 1:
                    hardPWM0.hardware_PWM(18,1,0)
                    break
        elif self.ids.togbtn6.state == "down":
            hardPWM0.hardware_PWM(19,1,1000000)
            while True:
                if hardPWM0.read(19) == 1:
                    hardPWM0.hardware_PWM(19,1,0)
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
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['pos']

        #get frequency and duty cycle values
        try:
            dc = float(temp[pos]['buttons'][0]['dc'])
            frq = float(temp[pos]['buttons'][0]['frq'])
        except:
            dc = frq = ""

        if temp[pos]['buttons'][0]['func'] == 'DC':
            if self.ids.btn0.state == "down":
                    p0.ChangeDutyCycle(100)
            elif self.ids.btn0.state == "normal":
                    p0.ChangeDutyCycle(0)
        if temp[pos]['buttons'][0]['func'] == 'PWM':
            try:
                p0.ChangeDutyCycle(dc)
                p0.ChangeFrequency(frq)
            except:
                pass
            if self.ids.btn0.state == "down":
                    p0.ChangeDutyCycle(dc)
            elif self.ids.btn0.state == "normal":
                    p0.ChangeDutyCycle(0)
        s.close()

    #outputs software pwm signals on raspberry pi when the button is pressed
    def btn1Out(self):

            #open database and save copy to temporary dictionary
            s = shelve.open('test1.db')
            temp = s['key1']
            pos = temp['pos']

            #get frequency and duty cycle values
            try:
                dc = float(temp[pos]['buttons'][1]['dc'])
                frq = float(temp[pos]['buttons'][1]['frq'])
            except:
                dc = frq = ""


            if temp[pos]['buttons'][1]['func'] == 'DC':
                if self.ids.btn1.state == "down":
                        p1.ChangeDutyCycle(100)
                elif self.ids.btn1.state == "normal":
                        p1.ChangeDutyCycle(0)
            if temp[pos]['buttons'][1]['func'] == 'PWM':
                try:
                    p1.ChangeDutyCycle(dc)
                    p1.ChangeFrequency(frq)
                except:
                    pass
                if self.ids.btn1.state == "down":
                        p1.ChangeDutyCycle(dc)
                elif self.ids.btn1.state == "normal":
                        p1.ChangeDutyCycle(0)
            s.close()

    #outputssoftware  pwm signals on raspberry pi when the button is pressed
    def btn2Out(self):

            #open database and save copy to temporary dictionary
            s = shelve.open('test1.db')
            temp = s['key1']
            pos = temp['pos']

            #get frequency and duty cycle values
            try:
                dc = float(temp[pos]['buttons'][2]['dc'])
                frq = float(temp[pos]['buttons'][2]['frq'])
            except:
                dc = frq = ""


            if temp[pos]['buttons'][2]['func'] == 'DC':
                if self.ids.btn2.state == "down":
                        p2.ChangeDutyCycle(100)
                elif self.ids.btn2.state == "normal":
                        p2.ChangeDutyCycle(0)
            if temp[pos]['buttons'][2]['func'] == 'PWM':
                try:
                    p2.ChangeDutyCycle(dc)
                    p2.ChangeFrequency(frq)
                except:
                    pass
                if self.ids.btn2.state == "down":
                        p2.ChangeDutyCycle(dc)
                elif self.ids.btn2.state == "normal":
                        p2.ChangeDutyCycle(0)
            s.close()

    #outputs software pwm signals on raspberry pi when the button is pressed
    def btn3Out(self):

            #open database and save copy to temporary dictionary
            s = shelve.open('test1.db')
            temp = s['key1']
            pos = temp['pos']

            #get frequency and duty cycle values
            try:
                dc = float(temp[pos]['buttons'][3]['dc'])
                frq = float(temp[pos]['buttons'][3]['frq'])
            except:
                dc = frq = ""


            if temp[pos]['buttons'][3]['func'] == 'DC':
                if self.ids.btn3.state == "down":
                        p3.ChangeDutyCycle(100)
                elif self.ids.btn3.state == "normal":
                        p3.ChangeDutyCycle(0)
            if temp[pos]['buttons'][3]['func'] == 'PWM':
                try:
                    p3.ChangeDutyCycle(dc)
                    p3.ChangeFrequency(frq)
                except:
                    pass
                if self.ids.btn3.state == "down":
                        p3.ChangeDutyCycle(dc)
                elif self.ids.btn3.state == "normal":
                        p3.ChangeDutyCycle(0)
            s.close()

    #outputs software pwm signals on raspberry pi when the button is pressed
    def btn4Out(self):

            #open database and save copy to temporary dictionary
            s = shelve.open('test1.db')
            temp = s['key1']
            pos = temp['pos']

            #get frequency and duty cycle values
            try:
                dc = float(temp[pos]['buttons'][4]['dc'])
                frq = float(temp[pos]['buttons'][4]['frq'])
            except:
                dc = frq = ""


            if temp[pos]['buttons'][4]['func'] == 'DC':
                if self.ids.btn4.state == "down":
                        p4.ChangeDutyCycle(100)
                elif self.ids.btn4.state == "normal":
                        p4.ChangeDutyCycle(0)
            if temp[pos]['buttons'][4]['func'] == 'PWM':
                try:
                    p4.ChangeDutyCycle(dc)
                    p4.ChangeFrequency(frq)
                except:
                    pass
                if self.ids.btn4.state == "down":
                        p4.ChangeDutyCycle(dc)
                elif self.ids.btn4.state == "normal":
                        p4.ChangeDutyCycle(0)
            s.close()

    #outputs hardware pwm signals on raspberry pi when the button is pressed
    def btn5Out(self):
        #open database and save copy to temporary dictionary
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['pos']

        #get frequency and duty cycle values
        #TODO: do better exception handling lol
        try:
            dc = 10000 * int(temp[pos]['buttons'][5]['dc'])
            frq = int(temp[pos]['buttons'][5]['frq'])
        except:
            dc = frq = ""

        if temp[pos]['buttons'][5]['func'] == 'DC':
            if self.ids.btn5.state == "down":
                    hardPWM0.hardware_PWM(18,1,1000000)
            elif self.ids.btn5.state == "normal":
                    hardPWM0.hardware_PWM(18,1,0)

        if temp[pos]['buttons'][5]['func'] == 'PWM':
            frq = int(frq)
            if self.ids.btn5.state == "down":
                    hardPWM0.hardware_PWM(18,frq,dc)
            elif self.ids.btn5.state == "normal":
                    hardPWM0.hardware_PWM(18,1,0)
        s.close()

    #outputs hardware signals on raspberry pi when the button is pressed
    def btn6Out(self):
        #open database and save copy to temporary dictionary
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['pos']

        #get frequency and duty cycle values
        #TODO: do better exception handling lol
        try:
            dc = 10000 * int(temp[pos]['buttons'][6]['dc'])
            frq = int(temp[pos]['buttons'][6]['frq'])
        except:
            dc = frq = ""

        if temp[pos]['buttons'][6]['func'] == 'DC':
            if self.ids.btn6.state == "down":
                    hardPWM0.hardware_PWM(19,1,1000000)
            elif self.ids.btn6.state == "normal":
                    hardPWM0.hardware_PWM(19,1,0)

        if temp[pos]['buttons'][6]['func'] == 'PWM':
            frq = int(frq)
            if self.ids.btn6.state == "down":
                    hardPWM0.hardware_PWM(19,frq,dc)
            elif self.ids.btn6.state == "normal":
                    hardPWM0.hardware_PWM(19,1,0)
        s.close()

class NewProgScreen0(Screen):
    #Upon pressing Next, commits the new program title at a new key in the dict
    #Also initializes the dict
    #Dict Structure is documented in OneNote under User Interface Design
    def commitNewProgTitle(self):
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['maxpos']
        pos = pos + 1
        temp[pos] = {'title':self.ids.entry.text, 'buttons':{0:{'title':'0','func':'DC','frq':100,'dc':101},1:{'title':'0','func':'DC','frq':100,'dc':101},2:{'title':'0','func':'DC','frq':100,'dc':101},3:{'title':'0','func':'DC','frq':100,'dc':101},4:{'title':'0','func':'DC','frq':100,'dc':101},5:{'title':'0','func':'DC','frq':100,'dc':101},6:{'title':'0','func':'DC','frq':100,'dc':101}}}
        temp['pos'] = pos
        temp['maxpos'] = pos
        s['key1'] = temp
        s.close()

    def updateText(self):
        self.ids.entry.text = "..."
        return "..."

class NewProgScreen1(Screen):
    def getbtn0State(self): #determine the button type (either DC or PWM)
        return self.ids.check0.state == "down"

    def getbtn1State(self):#determine the button type (either DC or PWM)
        return self.ids.check1.state == "down"

    def getbtn2State(self):#determine the button type (either DC or PWM)
        return self.ids.check2.state == "down"

    def getbtn3State(self):#determine the button type (either DC or PWM)
        return self.ids.check3.state == "down"

    def getbtn4State(self):#determine the button type (either DC or PWM)
        return self.ids.check4.state == "down"

    def getbtn5State(self):#determine the button type (either DC or PWM)
        return self.ids.check5.state == "down"

    def getbtn6State(self):#determine the button type (either DC or PWM)
        return self.ids.check6.state == "down"



    def updatefrqtxt0State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt0.disabled = self.getbtn0State()
        if self.getbtn0State() == True:
            self.ids.frqtxt0.text = ""
            self.ids.frqtxt0.background_color = [1,1,1,1]

    def updatefrqtxt1State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt1.disabled = self.getbtn1State()
        if self.getbtn1State() == True:
            self.ids.frqtxt1.text = ""
            self.ids.frqtxt1.background_color = [1,1,1,1]

    def updatefrqtxt2State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt2.disabled = self.getbtn2State()
        if self.getbtn2State() == True:
            self.ids.frqtxt2.text = ""
            self.ids.frqtxt2.background_color = [1,1,1,1]

    def updatefrqtxt3State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt3.disabled = self.getbtn3State()
        if self.getbtn3State() == True:
            self.ids.frqtxt3.text = ""
            self.ids.frqtxt3.background_color = [1,1,1,1]

    def updatefrqtxt4State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt4.disabled = self.getbtn4State()
        if self.getbtn4State() == True:
            self.ids.frqtxt4.text = ""
            self.ids.frqtxt4.background_color = [1,1,1,1]

    def updatefrqtxt5State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt5.disabled = self.getbtn5State()
        if self.getbtn5State() == True:
            self.ids.frqtxt5.text = ""
            self.ids.frqtxt5.background_color = [1,1,1,1]

    def updatefrqtxt6State(self): #disable text inputs if the DC option is chosen in drop down menu
        self.ids.frqtxt6.disabled = self.getbtn6State()
        if self.getbtn6State() == True:
            self.ids.frqtxt6.text = ""
            self.ids.frqtxt6.background_color = [1,1,1,1]


    def updatedctxt0State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt0.disabled = self.getbtn0State()
        if self.getbtn0State() == True:
            self.ids.dctxt0.text = ""
            self.ids.dctxt0.background_color = [1,1,1,1]

    def updatedctxt1State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt1.disabled = self.getbtn1State()
        if self.getbtn1State() == True:
            self.ids.dctxt1.text = ""
            self.ids.dctxt1.background_color = [1,1,1,1]

    def updatedctxt2State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt2.disabled = self.getbtn2State()
        if self.getbtn2State() == True:
            self.ids.dctxt2.text = ""
            self.ids.dctxt2.background_color = [1,1,1,1]

    def updatedctxt3State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt3.disabled = self.getbtn3State()
        if self.getbtn3State() == True:
            self.ids.dctxt3.text = ""
            self.ids.dctxt3.background_color = [1,1,1,1]

    def updatedctxt4State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt4.disabled = self.getbtn4State()
        if self.getbtn4State() == True:
            self.ids.dctxt4.text = ""
            self.ids.dctxt4.background_color = [1,1,1,1]

    def updatedctxt5State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt5.disabled = self.getbtn5State()
        if self.getbtn5State() == True:
            self.ids.dctxt5.text = ""
            self.ids.dctxt5.background_color = [1,1,1,1]

    def updatedctxt6State(self):#disable text inputs if the DC option is chosen in drop down menu
        self.ids.dctxt6.disabled = self.getbtn6State()
        if self.getbtn6State() == True:
            self.ids.dctxt6.text = ""
            self.ids.dctxt6.background_color = [1,1,1,1]

    #put all the info entered into the textinputs into the dictionary and store in in the shelve database
    def commitButtonInfo(self):
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['pos']
        temp[pos]['buttons'][0]['title'] = self.ids.btntxt0.text
        temp[pos]['buttons'][1]['title'] = self.ids.btntxt1.text
        temp[pos]['buttons'][2]['title'] = self.ids.btntxt2.text
        temp[pos]['buttons'][3]['title'] = self.ids.btntxt3.text
        temp[pos]['buttons'][4]['title'] = self.ids.btntxt4.text
        temp[pos]['buttons'][5]['title'] = self.ids.btntxt5.text
        temp[pos]['buttons'][6]['title'] = self.ids.btntxt6.text

        if self.ids.check0.state == "down":
            temp[pos]['buttons'][0]['func'] = "DC"
        else:
            temp[pos]['buttons'][0]['func'] = "PWM"

        if self.ids.check1.state == "down":
            temp[pos]['buttons'][1]['func'] = "DC"
        else:
            temp[pos]['buttons'][1]['func'] = "PWM"

        if self.ids.check2.state == "down":
            temp[pos]['buttons'][2]['func'] = "DC"
        else:
            temp[pos]['buttons'][2]['func'] = "PWM"

        if self.ids.check3.state == "down":
            temp[pos]['buttons'][3]['func'] = "DC"
        else:
            temp[pos]['buttons'][3]['func'] = "PWM"

        if self.ids.check4.state == "down":
            temp[pos]['buttons'][4]['func'] = "DC"
        else:
            temp[pos]['buttons'][4]['func'] = "PWM"

        if self.ids.check5.state == "down":
            temp[pos]['buttons'][5]['func'] = "DC"
        else:
            temp[pos]['buttons'][5]['func'] = "PWM"

        if self.ids.check6.state == "down":
            temp[pos]['buttons'][6]['func'] = "DC"
        else:
            temp[pos]['buttons'][6]['func'] = "PWM"

        temp[pos]['buttons'][0]['frq'] = self.ids.frqtxt0.text
        temp[pos]['buttons'][1]['frq'] = self.ids.frqtxt1.text
        temp[pos]['buttons'][2]['frq'] = self.ids.frqtxt2.text
        temp[pos]['buttons'][3]['frq'] = self.ids.frqtxt3.text
        temp[pos]['buttons'][4]['frq'] = self.ids.frqtxt4.text
        temp[pos]['buttons'][5]['frq'] = self.ids.frqtxt5.text
        temp[pos]['buttons'][6]['frq'] = self.ids.frqtxt6.text

        temp[pos]['buttons'][0]['dc'] = self.ids.dctxt0.text
        temp[pos]['buttons'][1]['dc'] = self.ids.dctxt1.text
        temp[pos]['buttons'][2]['dc'] = self.ids.dctxt2.text
        temp[pos]['buttons'][3]['dc'] = self.ids.dctxt3.text
        temp[pos]['buttons'][4]['dc'] = self.ids.dctxt4.text
        temp[pos]['buttons'][5]['dc'] = self.ids.dctxt5.text
        temp[pos]['buttons'][6]['dc'] = self.ids.dctxt6.text
        s['key1'] = temp
        s.close()

    #resets the data/state of all the text inputs and buttons so old data is not displayed on them
    def updateWidgets(self):
        s = shelve.open('test1.db')
        temp = s['key1']
        pos = temp['pos']

        #temp['del'] == 1 means the screen is in edit program mode, so it displays the current programs information
        if temp['del'] == 1:
            self.ids.btntxt0.text = temp[pos]['buttons'][0]['title']
            self.ids.btntxt1.text = temp[pos]['buttons'][1]['title']
            self.ids.btntxt2.text = temp[pos]['buttons'][2]['title']
            self.ids.btntxt3.text = temp[pos]['buttons'][3]['title']
            self.ids.btntxt4.text = temp[pos]['buttons'][4]['title']
            self.ids.btntxt5.text = temp[pos]['buttons'][5]['title']
            self.ids.btntxt6.text = temp[pos]['buttons'][6]['title']

            self.ids.frqtxt0.text = temp[pos]['buttons'][0]['frq']
            self.ids.frqtxt1.text = temp[pos]['buttons'][1]['frq']
            self.ids.frqtxt2.text = temp[pos]['buttons'][2]['frq']
            self.ids.frqtxt3.text = temp[pos]['buttons'][3]['frq']
            self.ids.frqtxt4.text = temp[pos]['buttons'][4]['frq']
            self.ids.frqtxt5.text = temp[pos]['buttons'][5]['frq']
            self.ids.frqtxt6.text = temp[pos]['buttons'][6]['frq']

            self.ids.dctxt0.text = temp[pos]['buttons'][0]['dc']
            self.ids.dctxt1.text = temp[pos]['buttons'][1]['dc']
            self.ids.dctxt2.text = temp[pos]['buttons'][2]['dc']
            self.ids.dctxt3.text = temp[pos]['buttons'][3]['dc']
            self.ids.dctxt4.text = temp[pos]['buttons'][4]['dc']
            self.ids.dctxt5.text = temp[pos]['buttons'][5]['dc']
            self.ids.dctxt6.text = temp[pos]['buttons'][6]['dc']

            if temp[pos]['buttons'][0]['func'] == "DC":
                self.ids.frqtxt0.disabled = True
                self.ids.dctxt0.disabled = True
                self.ids.check0.active = True

            if temp[pos]['buttons'][1]['func'] == "DC":
                self.ids.frqtxt1.disabled = True
                self.ids.dctxt1.disabled = True
                self.ids.check1.active = True

            if temp[pos]['buttons'][2]['func'] == "DC":
                self.ids.frqtxt2.disabled = True
                self.ids.dctxt2.disabled = True
                self.ids.check2.active = True

            if temp[pos]['buttons'][3]['func'] == "DC":
                self.ids.frqtxt3.disabled = True
                self.ids.dctxt3.disabled = True
                self.ids.check3.active = True

            if temp[pos]['buttons'][4]['func'] == "DC":
                self.ids.frqtxt4.disabled = True
                self.ids.dctxt4.disabled = True
                self.ids.check4.active = True

            if temp[pos]['buttons'][5]['func'] == "DC":
                self.ids.frqtxt5.disabled = True
                self.ids.dctxt5.disabled = True
                self.ids.check5.active = True

            if temp[pos]['buttons'][6]['func'] == "DC":
                self.ids.frqtxt6.disabled = True
                self.ids.dctxt6.disabled = True
                self.ids.check6.active = True

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
        else:
            self.ids.btntxt0.text = ""
            self.ids.btntxt1.text = ""
            self.ids.btntxt2.text = ""
            self.ids.btntxt3.text = ""
            self.ids.btntxt4.text = ""
            self.ids.btntxt5.text = ""
            self.ids.btntxt6.text = ""

            self.ids.frqtxt0.text = ""
            self.ids.frqtxt1.text = ""
            self.ids.frqtxt2.text = ""
            self.ids.frqtxt3.text = ""
            self.ids.frqtxt4.text = ""
            self.ids.frqtxt5.text = ""
            self.ids.frqtxt6.text = ""

            self.ids.frqtxt0.disabled = True
            self.ids.frqtxt1.disabled = True
            self.ids.frqtxt2.disabled = True
            self.ids.frqtxt3.disabled = True
            self.ids.frqtxt4.disabled = True
            self.ids.frqtxt5.disabled = True
            self.ids.frqtxt6.disabled = True

            self.ids.dctxt0.text = ""
            self.ids.dctxt1.text = ""
            self.ids.dctxt2.text = ""
            self.ids.dctxt3.text = ""
            self.ids.dctxt4.text = ""
            self.ids.dctxt5.text = ""
            self.ids.dctxt6.text = ""

            self.ids.dctxt0.disabled = True
            self.ids.dctxt1.disabled = True
            self.ids.dctxt2.disabled = True
            self.ids.dctxt3.disabled = True
            self.ids.dctxt4.disabled = True
            self.ids.dctxt5.disabled = True
            self.ids.dctxt6.disabled = True

            self.ids.check0.active = True
            self.ids.check1.active = True
            self.ids.check2.active = True
            self.ids.check3.active = True
            self.ids.check4.active = True
            self.ids.check5.active = True
            self.ids.check6.active = True

            self.ids.check00.active = False
            self.ids.check11.active = False
            self.ids.check22.active = False
            self.ids.check33.active = False
            self.ids.check44.active = False
            self.ids.check55.active = False
            self.ids.check66.active = False

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
        if self.ids.check0.active == False:

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
        if self.ids.check1.active == False:

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
        if self.ids.check2.active == False:

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
        if self.ids.check3.active == False:

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
        if self.ids.check4.active == False:

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
        if self.ids.check5.active == False:

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
        if self.ids.check6.active == False:

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
            return "newprog1"

class ScreenManagement(ScreenManager):
    pass

class MainApp(App):

    def build(self):
        presentation = Builder.load_file("kivy.kv")
        return presentation

if __name__ == "__main__":
    MainApp().run()
