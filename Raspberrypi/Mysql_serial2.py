import serial
import mysql.connector
import time

ser=serial.Serial('/dev/ttyAMA3',9600) #reset serial port
while True:
    data=ser.readline().decode('UTF-8').rstrip().split(',')
    print(data)
