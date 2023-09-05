import mysql.connector

cnx = mysql.connector.connect(
                  host='bifrost0602.duckdns.org',
                  user='TEST',
                  port=2024,
                  password='1234',
                 database='CANSATDB'
              )
              
cursor = cnx.cursor()
print('query go')
query = 'SELECT elapsed_time, ax, ay, az, gx, gy, gz, angx, angy, HEADING, temp, pressure, alt, lat, longi, gpsalt, light FROM SENSOR ORDER BY elapsed_time DESC LIMIT 1'
cursor.execute(query)
print('query end')
row = self.cursor.fetchone()
elapsed_time, ax, ay, az, gx, gy, gz, angx, angy, HEADING, temp, pressure, alt, lat, longi, gpsalt, light=row
print(elapsed_time, ax, ay, az, gx, gy, gz, angx, angy, HEADING, temp, pressure, alt, lat, longi, gpsalt,light)
cnx.close()
print('cnx close')
# Write results to text file
print('answer:'+row)
