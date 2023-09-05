import mysql.connector
import subprocess


while True:
    try:
        cnx = mysql.connector.connect(
            host='bifrost0602.duckdns.org',
            user='TEST',
            port=2024,
            password='1234',
            database='CANSATDB'
        )

        cursor = cnx.cursor()

        cursor.execute("SELECT command FROM COMMANDS ORDER BY time DESC LIMIT 1")

        result = cursor.fetchone()

        cnx.commit()
        cnx.close()
        
        print('waiting....\n')
                    
        if result and result[0] == 'start':
            while True:
                try:
                    subprocess.call(['python','/home/cnu/tflite1/cansat.py'])
                    break
                except:
                    pass
    except Exception as e:
        pass
