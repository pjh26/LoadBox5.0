from smbus2 import SMBus
import RPi.GPIO as GPIO
import math
import time
import spidev

bus = SMBus(1)
GPIO.setmode(GPIO.BCM)

# Setup function
GPIO.setup(20, GPIO.OUT)

# Setup select
GPIO.setup(21, GPIO.OUT) # Current Select 0
GPIO.setup(26, GPIO.OUT) # Current Select 1
GPIO.setup(4, GPIO.OUT)  # Current Select 2

GPIO.setup(22, GPIO.OUT) # Slew Select 0
GPIO.setup(27, GPIO.OUT) # Slew Select 1
GPIO.setup(17, GPIO.OUT) # Slew Select 2

# Setup spi bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 15600000

def stdev(list):
	length = len(list)
	average = sum(list)/length
	sumavg = 0

	for i in range(length):
		sumavg += (list[i] - average) ** 2

	return math.sqrt(sumavg / (length-1))

def testVccMeasurement():
	numsum = 0
	for i in range(100):
		read = bus.read_i2c_block_data(82, 0, 2)
		total = (read[0] << 8) + read[1]
		numsum += total
		#print(read)
		#print(total)
	voltage = ((numsum/100) - 53.271) / 110.42
	print(numsum/100)
	print(voltage)

def testCurrentMeasurement():
	numsum = 0
	GPIO.output(20, 1)

	GPIO.output(21, 1)
	GPIO.output(26, 0)
	GPIO.output(4, 0)

	time.sleep(0.1)
	for i in range(100):
		read = bus.read_i2c_block_data(84, 0, 2)
		total = (read[0] << 8) + read[1]
		numsum += total
		#print(read)
		#print(total)

	GPIO.output(20, 0)
	current = ((numsum/100) * 0.003) - 1.2202
	print(numsum/100)
	print(current)

def I2CBus():
	while True:
		read = bus.read_i2c_block_data(80, 0, 2)
		time.sleep(0.2)

		total = (read[1] << 8) + read[0]
		print(total)
		if total == 0:
			print("ERROR!")




def testSlewRateMeasurement(num):
	numsum = 0
	numlist = []

	GPIO.output(22, 1)
	GPIO.output(27, 0)
	GPIO.output(17, 0)

	if num == '':
		spi.writebytes([0, 0])
	else:
		spi.writebytes([0, int(num)])
	time.sleep(0.1)

	# Read Vcc Value
	for i in range(100):
		read = bus.read_i2c_block_data(82, 0, 2)
		total = (read[0] << 8) + read[1]
		numsum += total

#	Vcc = ((numsum/100) - 53.271) * 0.00905633
	Vcc = 12
	Vchange = (Vcc * 0.8939) - (Vcc * 0.1443)
	print("Voltage:    " + str(Vcc))

	numsum = 0
	numlist = []

	for i in range(1):
		GPIO.output(20, 1)
		time.sleep(0.001)

		read = bus.read_i2c_block_data(80, 0, 2)

		GPIO.output(20, 0)
		time.sleep(0.001)

		total = (read[0] << 8) + read[1]

		numsum += total
		numlist.append(total)
		#print(read)
		#print(total)


	usec = 0
	usec = (0.0451 * (numsum/1)) - 0.3279
	slewrate = Vchange/usec
	print("TMR Value:  " + str(numsum/1))
#	print("Time stdev: " + str(stdev(numlist)))
	print("Avg time:   " + str(usec))
	print("Calc Slew Rate: " + str(slewrate) + "\n")


while True:
	print("Press enter to measure")
	input = input()
	if (input == "q"):
		break
	else:
		#testVccMeasurement()
		#testCurrentMeasurement()
		#testSlewRateMeasurement(input)
		I2CBus()

GPIO.cleanup()
