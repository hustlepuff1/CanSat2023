import threading
import time
import os
import glob
import mysql.connector
import pandas as pd
import queue
from ftplib import FTP

from Mysql_serial import CANSAT_Serial
from camera_ftp import shot, Od
import blue


class CANSATSystem:
    def __init__(self):
        self.stop_event = threading.Event()
        self.num = 1
        self.ftpnum = 1
        self.control_start = False
        self.data_queue = queue.Queue()

        # MySQL server details
        self.MYSQL_HOST = "bifrost0602.duckdns.org"
        self.MYSQL_PORT = 2024
        self.MYSQL_USER = "TEST"
        self.MYSQL_PASSWORD = "1234"
        self.MYSQL_DATABASE = "CANSATDB"

        # FTP server details
        self.FTP_SERVER = "bifrost0602.duckdns.org"
        self.FTP_USERNAME = "bifrost"
        self.FTP_PASSWORD = "1234"
        self.FTP_PORT = 2025
        self.FTP_DIRECTORY = "/home/bifrost/Documents"

    def clean_ftp_directory(self):
        try:
            ftp = FTP()
            ftp.connect(self.FTP_SERVER, self.FTP_PORT)
            ftp.login(self.FTP_USERNAME, self.FTP_PASSWORD)
            ftp.cwd(self.FTP_DIRECTORY)

            for filename in ftp.nlst():
                try:
                    ftp.delete(filename)
                    print(f"Deleted {filename}")
                except Exception as e:
                    print(e)

            print("Directory cleaned")
        except Exception as e:
            print(f"FTP Error: {e}")

    def initialize_mysql(self):
        try:
            cnx = mysql.connector.connect(
                host=self.MYSQL_HOST,
                user=self.MYSQL_USER,
                port=self.MYSQL_PORT,
                password=self.MYSQL_PASSWORD,
                database=self.MYSQL_DATABASE
            )
            print('Connection Success')
            return cnx
        except mysql.connector.Error as err:
            print(f"MySQL Connection Error: {err}")
            return None

    def clean_image_directory(self):
        files = glob.glob('/home/cnu/tflite1/image/*')
        for f in files:
            os.remove(f)

    def start(self):
        try:
            self.clean_ftp_directory()
            self.clean_image_directory()
            cnx = self.initialize_mysql()
            if not cnx:
                return

            try:
                cursor = cnx.cursor()
                query = 'DELETE FROM SENSOR'
                cursor.execute(query)
                cnx.commit()
                cursor.close()
            except Exception as e:
                print(f"MySQL Query Error: {e}")

            try:
                thread1 = threading.Thread(target=self.cam_task)
                thread2 = threading.Thread(target=self.serial_task)
                thread3 = threading.Thread(target=self.check_input)
                thread4 = threading.Thread(target=self.ftp_task)
                thread5 = threading.Thread(target=self.csv_task)

                thread1.start()
                thread2.start()
                thread3.start()
                thread4.start()
                thread5.start()

                thread1.join()
                thread2.join()
                thread3.join()
                thread4.join()
                thread5.join()

                print('All threads stopped')
            except Exception as e:
                print(f"Thread Error: {e}")
        except Exception as e:
            print(f"Error occurred: {e}")

    def cam_task(self):
        while not self.stop_event.is_set():
            try:
                shot(self.num)
                self.num += 1
                time.sleep(1)
            except Exception as e:
                print(f"Camera Task Error: {e}")
        print('Camera Task stop')

    def serial_task(self):
        try:
            cnx = self.initialize_mysql()
            if not cnx:
                return

            try:
                cursor = cnx.cursor()
                start_time = time.time()
                elapsed_time = 0

                while not self.stop_event.is_set():
                    elapsed_time = time.time() - start_time
                    data = CANSAT_Serial(elapsed_time, self.stop_event, cnx, cursor)
                    self.data_queue.put(data)
                    light_ref = 300
                    try:
                        if int(data[-1]) < light_ref and not self.control_start:
                            query = "INSERT INTO COMMANDS (command) VALUES ('control start')"
                            cursor.execute(query)
                            self.control_start = True
                            cnx.commit()
                    except Exception as e:
                        print(e)
                    time.sleep(1)

                cursor.close()
            except Exception as e:
                print(f"Serial Task Error: {e}")
            finally:
                cnx.close()
        except mysql.connector.Error as err:
            print(f"MySQL Connection Error: {err}")
        print('Serial Task stop')

    def check_input(self):
        try:
            cnx = self.initialize_mysql()
            if not cnx:
                return

            while not self.stop_event.is_set():
                try:
                    cursor = cnx.cursor()
                    cursor.execute("SELECT command FROM COMMANDS ORDER BY time DESC LIMIT 1")
                    result = cursor.fetchone()
                    cnx.commit()

                    if result and result[0] == 'stop':
                        self.stop_event.set()
                        break
                    elif result and result[0] == 'control start':
                        blue.control_on()
                        self.control_start = True
                    elif result and result[0] == 'control stop':
                        blue.control_off()
                        self.control_start = False
                except Exception as e:
                    print(f"Check Input Error: {e}")
                    time.sleep(1)
            cnx.close()
        except mysql.connector.Error as err:
            print(f"MySQL Connection Error: {err}")
        print('Check Input stop')

    def ftp_task(self):
        
        #ftp connection
        ftp = FTP()
        ftp.connect('bifrost0602.duckdns.org', 2025)
        ftp.login('bifrost', '1234')
        print('FTP connection established')
        ftp.cwd('/home/bifrost/Documents')
        print('Directory changed')
        
        while not self.stop_event.is_set():
            try:
                Od(self.ftpnum)
            except Exception as e:
                print(f"FTP Task Error: {e}")
                continue
            self.ftpnum += 1
            
        ftp.quit()
        print('FTP Task stop')

    def csv_task(self):
        sensor_data = pd.DataFrame(columns=['now_time', 'elapsed_time', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'angx', 'angy', 'HEADING', 'temp', 'pressure', 'alt', 'lat', 'longi', 'gpsalt', 'light'])
        start_time = time.time()
        elapsed_time = 0
        try:
            while not self.stop_event.is_set():
                data = self.data_queue.get()
                now_time = time.time()
                elapsed_time = now_time - start_time
                try:
                    ax, ay, az, gx, gy, gz, angx, angy, heading, temp, press, alt, lati, longi, gpsalt, light = [float(i) for i in data]
                except:
                    ax, ay, az, gx, gy, gz, angx, angy, heading, temp, press, alt, lati, longi, gpsalt, light = [0.0] * 16

                # Add the data to the DataFrame
                sensor_data = pd.concat([sensor_data, pd.DataFrame([{'now_time': now_time, 'elapsed_time': elapsed_time, 'ax': ax, 'ay': ay, 'az': az, 'gx': gx, 'gy': gy, 'gz': gz, 'angx': angx, 'angy': angy, 'HEADING': heading, 'temp': temp, 'pressure': press, 'alt': alt, 'lat': lati, 'longi': longi, 'gpsalt': gpsalt, 'light': light}], index=[0])], ignore_index=True)
        except Exception as e:
            print(f"CSV Task Error: {e}")
        finally:
            # Save the DataFrame to a CSV file
            sensor_data.to_csv('/home/cnu/tflite1/Sensor_data/sensor_data.csv', index=False)
            print('CSV saved')


if __name__ == "__main__":
    cansat_system = CANSATSystem()
    cansat_system.start()
