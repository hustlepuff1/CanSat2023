import serial
import mysql.connector
import time

ser=serial.Serial('/dev/ttyAMA3',9600) #reset serial port

def CANSAT_Serial(elapsed_time,stop_event,cnx,cursor):
            light=0
            try:
                data=ser.readline().decode('UTF-8').rstrip().split(',')
                if len(data)==16:
                    ax,ay,az,gx,gy,gz,angx,angy,heading,temp,press,alt,lati,longi,gpsalt,light=[float(i) for i in data]
                    query = 'INSERT INTO SENSOR (elapsed_time,ax,ay,az,gx,gy,gz,angx,angy,HEADING,temp,pressure,alt,lat,longi,gpsalt,light) VALUES('+str(elapsed_time)+','+str(ax)+','+str(ay)+','+str(az)+','+str(gx)+','+str(gy)+','+str(gz)+','+str(angx)+','+str(angy)+','+str(heading)+','+str(temp)+','+str(press)+','+str(alt)+','+str(lati)+','+str(longi)+','+str(gpsalt)+','+str(light)+')'
                    cursor.execute(query)
                else:
                    query = "INSERT INTO FEEDBACK (CALIFEEDBACK) VALUES ('"+ "', '".join(data) +"')"
                    cursor.execute(query)
            except Exception as e:
                ax,ay,az,gx,gy,gz,angx,angy,heading,temp,press,alt,lati,longi,gpsalt,light=[0.0]*16
                try:
                    query = 'INSERT INTO SENSOR (elapsed_time,ax,ay,az,gx,gy,gz,angx,angy,HEADING,temp,pressure,alt,lat,longi,gpsalt,light) VALUES('+str(elapsed_time)+','+str(ax)+','+str(ay)+','+str(az)+','+str(gx)+','+str(gy)+','+str(gz)+','+str(angx)+','+str(angy)+','+str(heading)+','+str(temp)+','+str(press)+','+str(alt)+','+str(lati)+','+str(longi)+','+str(gpsalt)+','+str(light)+')'
                    cursor.execute(query)
                except:
                    pass
            try:        
                cnx.commit()
            except:
                pass
            return data
