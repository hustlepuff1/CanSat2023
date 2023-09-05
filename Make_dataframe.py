import serial
import pandas as pd
import time

ser=serial.Serial('/dev/ttyAMA3',9600) #reset serial port

# Initialize DataFrame with specified columns
data_columns = ['ax','ay','az','gx','gy','gz','mx','my','mz','temp','press','alt','lat','longi','gpsalt', 'Light', 'Heading']
df = pd.DataFrame(columns=data_columns)

while True:
	data=ser.readline().decode('ascii').rstrip().split(',')
	if len(data)!=17:
		continue
	ax,ay,az,gx,gy,gz,mx,my,mz,heading,temp,press,alt,lati,longi,gpsalt,light=[float(i) for i in data]
	if light>900:
		print('측정 시작!')
		start_time=time.time()
		elapsed_time=0
		break

while True:
	data=ser.readline().decode('ascii').rstrip().split(',')
	if len(data)!=17:
		continue
	ax,ay,az,gx,gy,gz,mx,my,mz,heading,temp,press,alt,lati,longi,gpsalt,light=[float(i) for i in data]
	if elapsed_time>10 and light>900:
		break
	# Create dictionary from data
	data_dict = {
		'ax': ax,
		'ay': ay,
		'az': az,
		'gx': gx,
		'gy': gy,
		'gz': gz,
		'mx': mx,
		'my': my,
		'mz': mz,
		'temp': temp,
		'press': press,
		'alt':alt,
		'lati':lati,
		'longi':longi,
		'gpsalt':gpsalt,
		'Light': light,
		'Heading': heading
	}
	
	# Get current time as datetime object
	elapsed_time = time.time() - start_time
	# Append data to DataFrame
	df.loc[elapsed_time] = data_dict

# Save DataFrame to CSV file when done
df.to_csv('/home/cnu/tflite1/Sensor_data/sensor_data2.csv')
