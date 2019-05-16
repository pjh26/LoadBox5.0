from __future__ import division
import pigpio

class GPIO_Timer:
    def __init__(self,gpio1,gpio2):
        self.pi = pigpio.pi()
        self.gpio1 = gpio1
        self.gpio2 = gpio2

    #tick is current time in useconds
    def cbf1(self,gpio,level,tick):
        self.time1 = tick

    #tick is current time in useconds
    def cbf2(self,gpio,level,tick):
        self.time2 = tick

    #return difference between the RISING_EDGE event times in seconds
    def getElapsedTime(self):
        try:
            time = (self.time2-self.time1)
        except AttributeError:
            time = -1
        return time

    def startCallBack(self):
        #callback function calls cbf1() when a rising edge is detected on pin gpio1
        self.cb1 = self.pi.callback(self.gpio1, pigpio.RISING_EDGE, self.cbf1)
        self.cb2 = self.pi.callback(self.gpio2, pigpio.RISING_EDGE, self.cbf2)
