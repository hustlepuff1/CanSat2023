import serial
import mysql.connector
import time

ser=serial.Serial('/dev/ttyAMA3',9600) #reset serial port

while True:
	try:
		# MySQL 서버에 연결합니다.
		cnx = mysql.connector.connect(
			host='bifrost0602.duckdns.org',
			user='TEST',
			port=2024,
			password='1234',
			database='CANSATDB'
		)

		print('Connection Success')

		# 커서를 생성합니다.
		cursor = cnx.cursor()

		#테스트 테이블 초기화
		query='DELETE FROM SENSOR'
		cursor.execute(query)
		cnx.commit()

		start_time=time.time()
		elapsed_time=0
		light=0

		while True:
			try:
				data=ser.readline().decode('ASCII').rstrip().split(',')
				if len(data)!=17:
					continue
				
				elapsed_time = time.time() - start_time
			
				ax,ay,az,gx,gy,gz,mx,my,mz,heading,temp,press,alt,lati,longi,gpsalt,light=[float(i) for i in data]
				
			except Exception as e:
				elased_time = time.time() - start_time
				ax,ay,az,gx,gy,gz,mx,my,mz,heading,temp,press,alt,lati,longi,gpsalt,light=[0.0]*17
			
			# SQL query start
			query = 'INSERT INTO SENSOR (elapsed_time,ax,ay,az,gx,gy,gz,mx,my,mz,temp,pressure,alt,lat,longi,gpsalt,light,Heading) VALUES('+str(elapsed_time)+','+str(ax)+','+str(ay)+','+str(az)+','+str(gx)+','+str(gy)+','+str(gz)+','+str(mx)+','+str(my)+','+str(mz)+','+str(temp)+','+str(press)+','+str(alt)+','+str(lati)+','+str(longi)+','+str(gpsalt)+','+str(light)+','+str(heading)+')'
			cursor.execute(query)
			
			# 변경사항을 데이터베이스에 반영 (인설트, 딜리트 등 변경사항이 있는 쿼리실행시 필수!)
			cnx.commit()

		print('Connention End')
		# 연결을 닫습니다.
		cursor.close()
		cnx.close()
		break
		
	except mysql.connector.Error as err:
		print(f"Something went wrong: {err}")
		time.sleep(5)  # Wait for 5 seconds before reattempting a connection
