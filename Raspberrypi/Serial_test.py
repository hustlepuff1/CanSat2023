import serial
import time

ser = serial.Serial('/dev/ttyAMA3', 9600)  # open serial port
ser.reset_input_buffer()

while True:
	data=ser.readline().decode('UTF-8').rstrip().split(',')
	print(data)
	
