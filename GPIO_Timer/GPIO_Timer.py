from __future__ import division
import pigpio

class GPIO_Timer:
    def __init__(self,gpio1,gpio2):
        self.pi = pigpio.pi()
        self.gpio1 = gpio1
        self.gpio2 = gpio2

    #tick is current time in useconds
    def cbRise1(self,gpio,level,tick):
        self.riseTime1 = tick

    #tick is current time in useconds
    def cbRise2(self,gpio,level,tick):
        self.riseTime2 = tick

    #tick is current time in useconds
    def cbFall1(self,gpio,level,tick):
        self.fallTime1 = tick

    #tick is current time in useconds
    def cbRFall2(self,gpio,level,tick):
        self.fallTime2 = tick

    #return difference between the RISING_EDGE event times in seconds
    def getElapsedTime(self, riseOrFall):
        try:
            riseTime = (self.riseTime2-self.riseTime1)
            fallTime = (self.fallTime2-self.fallTime2)
        except AttributeError:
            riseTime = -1
            fallTime = -1

        if (riseOrFall == 'rise'):
            return riseTime
        elif (riseOrFall == 'fall'):
            return fallTime
        else:
            return -1

    def startCallBack(self):
        #callback function calls cbf1() when a rising edge is detected on pin gpio1
        self.cb1 = self.pi.callback(self.gpio1, pigpio.RISING_EDGE, self.cbRise1)
        self.cb2 = self.pi.callback(self.gpio2, pigpio.RISING_EDGE, self.cbRise2)
        self.cb3 = self.pi.callback(self.gpio1, pigpio.FALLING_EDGE, self.cbFall1)
        self.cb4 = self.pi.callback(self.gpio2, pigpio.FALLING_EDGE, self.cbFall2)
