import serial

ser=serial.Serial('/dev/ttyAMA3',9600) #reset serial port

while True:
	data=ser.readline().decode('ASCII').rstrip().split(',')
	if len(data)!=17:
		continue
	ax,ay,az,gx,gy,gz,mx,my,mz,heading,temp,press,alt,lati,longi,gpsalt,light=[float(i) for i in data]
	print('Axyz: ',ax,', ',ay,', ',az,'\n')
	print('Gxyz: ',gx,', ',gy,', ',gz,'\n')
	print('Mxyz: ',mx,', ',my,', ',mz,'\n')
	print('T,P,A: ',temp,', ',press,', ',alt,'\n')
	print('GPS: ',lati,', ',longi, ', ', gpsalt, '\n')
	print('Light: ',light,'\n')
	print('Heading: ',heading,'\n')
	
	print('------------------------')
