import serial
import mysql.connector
import time
import signal
import sys

ser = serial.Serial('/dev/ttyAMA3', 9600)  # Reset serial port
exit_flag = False


def signal_handler(signal, frame):
    global exit_flag
    print("\nReceived Ctrl+C. Exiting gracefully...")
    exit_flag = True


def CANSAT_Serial():
    global exit_flag
    while not exit_flag:
        try:
            # Replace this section with actual data reading from the serial port
            # For demonstration purposes, we'll use dummy data here
            data = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"
            data = data.split(',')
            elapsed_time = time.time()
            ax, ay, az, gx, gy, gz, angx, angy, heading, temp, press, alt, lati, longi, gpsalt, light = [
                float(i) for i in data]

            # Database insertion code using the data received from the serial port
            cnx = mysql.connector.connect(
                host='bifrost0602.duckdns.org',
                user='TEST',
                port=2024,
                password='1234',
                database='CANSATDB'
            )
            cursor = cnx.cursor()
            query = 'INSERT INTO SENSOR (elapsed_time,ax,ay,az,gx,gy,gz,angx,angy,HEADING,temp,pressure,alt,lat,longi,gpsalt,light) VALUES('+str(elapsed_time)+','+str(ax)+','+str(ay)+','+str(az)+','+str(
                gx)+','+str(gy)+','+str(gz)+','+str(angx)+','+str(angy)+','+str(heading)+','+str(temp)+','+str(press)+','+str(alt)+','+str(lati)+','+str(longi)+','+str(gpsalt)+','+str(light)+')'
            cursor.execute(query)
            cnx.commit()
            cursor.close()
            cnx.close()

        except mysql.connector.Error as err:
            print(f"Something went wrong with database connection: {err}")
            # Wait for 5 seconds before reattempting a connection
            time.sleep(5)

        except Exception as e:
            print("An unexpected error occurred:", e)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    CANSAT_Serial()
