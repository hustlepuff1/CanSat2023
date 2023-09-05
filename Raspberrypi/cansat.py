## integration

#thread
import threading
import time
import os
import glob
import mysql.connector
import sys
import blue
import pandas as pd
import queue
from picamera2 import Picamera2
from libcamera import controls

# Create a Queue object
data_queue = queue.Queue()

#Serial
from Mysql_serial import CANSAT_Serial

#FTP
from camera_ftp import shot,Od

#logging
import logging

logging.basicConfig(filename='/home/cnu/tflite1/cansat.log', level=logging.INFO)

global stop_event
stop_event = threading.Event()

num=1
ftpnum=1

from ftplib import FTP

# FTP server details
FTP_SERVER = "bifrost0602.duckdns.org"
FTP_USERNAME = "bifrost"
FTP_PASSWORD = "1234"
FTP_PORT= 2025

# Directory to be cleaned
FTP_DIRECTORY = "/home/bifrost/Documents"

ftp_on=False

#Clean FTP Server
def clean_ftp_directory():
    global ftp_on
    while not ftp_on:
        try:
            # Connect to the FTP server
            ftp=FTP()

            ftp.connect(FTP_SERVER, FTP_PORT)
            ftp.login(FTP_USERNAME,FTP_PASSWORD)
            
            # Change to the directory to be cleaned
            ftp.cwd(FTP_DIRECTORY)
            ftp_on=True
        except Exception as e:
            print(f"Clean FTP Error: {e}")
            time.sleep(1)

    # Loop through each file in the directory
    for filename in ftp.nlst():

        # Delete the file
        try:
            ftp.delete(filename)
            print(f"Deleted {filename}")
        except Exception as e:
            print(e)

    print("Directory cleaned")

clean_ftp_directory()

#Clean Image Dir
files=glob.glob('/home/cnu/tflite1/image/*')

for f in files:
    os.remove(f)
    
# MySQL 서버에 연결합니다.
cnx = mysql.connector.connect(
    host='bifrost0602.duckdns.org',
    user='TEST',
    port=2024,
    password='1234',
    database='CANSATDB'
    )
                
print('MySQL Connection Success')

# 커서를 생성합니다.
cursor = cnx.cursor()

#테스트 테이블 초기화
query='DELETE FROM SENSOR'
cursor.execute(query)
cnx.commit()

cursor.close()
cnx.close()

control_start=False

def serial_task():
    global control_start
    while not stop_event.is_set():
        try:
            # MySQL 서버에 연결합니다.
            cnx = mysql.connector.connect(
                host='bifrost0602.duckdns.org',
                user='TEST',
                port=2024,
                password='1234',
                database='CANSATDB'
                )
                
            print('MySQL Connection Success')
            
            cursor = cnx.cursor()
            query="INSERT INTO FEEDBACK (FEEDBACK) VALUES ('CANSAT STARTED')"
            cursor.execute(query)
            cnx.commit()
            start_time=time.time()
            elapsed_time=0
            light_ref=800
            
            while not stop_event.is_set():
                elapsed_time=time.time()-start_time
                data=CANSAT_Serial(elapsed_time,stop_event,cnx,cursor)
                if len(data)==16:
                    data_queue.put(data)
                    if int(data[-1])<light_ref and control_start:
                        blue.control_on()
            cursor.close()
            cnx.close()
        except Exception as e:
                print(f"Mysql Error: {e}")
                print(f"Retrying Mysql connection...")
                time.sleep(1)
    print('serial stop')
        
def check_input():
    global control_start
    while not stop_event.is_set():
        try:
            cnx = mysql.connector.connect(
                    host='bifrost0602.duckdns.org',
                    user='check',
                    port=2024,
                    password='1234',
                    database='CANSATDB'
                )
            while not stop_event.is_set():
                    #print("Checking input...")
                    try:
                        cursor = cnx.cursor()
                        cnx.commit()
                        cursor.execute("SELECT command FROM COMMANDS ORDER BY time DESC LIMIT 1")
                        result = cursor.fetchone()
                        #print(f"result reseived: {result}")
                        if result != None:
                            if result and result[0] == 'stop':
                                stop_event.set()
                                break
                            elif result and result[0] == 'control start':
                                control_start=True
                            elif result and result[0] == 'control stop':
                                blue.control_off()
                                control_start=False
                        time.sleep(0.5)
                    except:
                        time.sleep(0.5)
                        pass
            cnx.close()
        except Exception as e:
            print(f"Check Error: {e}")
            print(f"Retrying Check...")
            time.sleep(1)
    print('check stop')
    
def cam_task():
    global num 
    while not stop_event.is_set():
        try:
            cnx = mysql.connector.connect(
                          host='bifrost0602.duckdns.org',
                          user='TEST',
                          port=2024,
                          password='1234',
                          database='CANSATDB'
                      )
            print("cnx complete")
            camera=None
            camera = Picamera2()
            config = camera.create_preview_configuration({"size": (1920, 1080)})
            config["main"]
            camera.align_configuration(config)
            camera.configure(config)
            camera.set_controls({"AfMode": controls.AfModeEnum.Continuous, "ExposureTime": 1000})
            camera.start()
            print("cam set complete")
            #Capture
            while not stop_event.is_set():
                #Cam Setting
                shot(cnx,camera,num)
                num+=1
                time.sleep(0.5)
            
            #Cam Close
            camera.stop()
            camera.close()
            
            cnx.close()
        except Exception as e:
            print(f"Cam Error: {e}")
            time.sleep(1)
    
    print('cam stop')
    

def ftp_task():
    while not stop_event.is_set():
        try:
            global ftpnum
            #ftp connection
            ftp = FTP()
            ftp.connect('bifrost0602.duckdns.org', 2025)
            ftp.login('bifrost', '1234')
            print('FTP connection established')
            ftp.cwd('/home/bifrost/Documents')
            print('Directory changed')
                
            while not stop_event.is_set():
                local_file_path_jpg = f'/home/cnu/tflite1/image/image{ftpnum+1}.jpg'
                if os.path.exists(local_file_path_jpg):
                    try:
                        Od(ftp,ftpnum)
                        time.sleep(0.5)
                    except:
                        continue
                    ftpnum += 1
            ftp.quit()
        except Exception as e:
            print(f"FTP Task Error: {e}")
            print("Retrying FTP Connection...")
            time.sleep(3)
    print('FTP Task stop')
    
def csv_task():
    try:
            sensor_data = pd.DataFrame(columns=['now_time','elapsed_time','ax','ay','az','gx','gy','gz','angx','angy','HEADING','temp','pressure','alt','lat','longi','gpsalt','light'])
            start_time = time.time()
            elapsed_time = 0
            while not stop_event.is_set():
                if not data_queue.empty():
                    data = data_queue.get()
                now_time = time.time()
                elapsed_time = now_time - start_time
                try:
                    ax,ay,az,gx,gy,gz,angx,angy,heading,temp,press,alt,lati,longi,gpsalt,light = [float(i) for i in data]
                except:
                    ax,ay,az,gx,gy,gz,angx,angy,heading,temp,press,alt,lati,longi,gpsalt,light = [0.0]*16

                    # Add the data to the DataFrame
                sensor_data = pd.concat([sensor_data, pd.DataFrame([{'now_time': now_time, 'elapsed_time': elapsed_time, 'ax': ax, 'ay': ay, 'az': az, 'gx': gx, 'gy': gy, 'gz': gz, 'angx': angx, 'angy': angy, 'HEADING': heading, 'temp': temp, 'pressure': press, 'alt': alt, 'lat': lati, 'longi': longi, 'gpsalt': gpsalt, 'light': light}], index=[0])], ignore_index=True)
    except Exception as e:
        print(f"CSV Error: {e}")
    finally:
        # Save the DataFrame to a CSV file
        try:
            sensor_data.to_csv('/home/cnu/tflite1/Sensor_data/sensor_data'+str(time.time())+'.csv', index=False)
        except Exception as e:
            print(e)
        print('csv saved')

    
try:
    #make thread
    thread1 = threading.Thread(target=cam_task)
    thread2 = threading.Thread(target=serial_task)
    thread3 = threading.Thread(target=check_input)
    thread4 = threading.Thread(target=ftp_task)
    thread5 = threading.Thread(target=csv_task)

    #thread start
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    
    #waiting untill threads end
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    
    print('all stop')

except Exception as e:
    print(f"Error occurred: {e}")
