import folium as g
from flask import Flask, render_template
import threading
import mysql.connector
import time

app = Flask(__name__)


def update_markers():
    while True:
        try:
            connection = mysql.connector.connect(
                host='bifrost0602.duckdns.org',
                user='TEST',
                password='1234',
                database='CANSATDB',
                port=2024
            )
            
            cursor = connection.cursor()
            sql = "SELECT `longi`, `lat` FROM `SENSOR` ORDER BY `TIME` DESC LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchall()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            connection.close()

        for (longi, lat) in result:
            g_map = g.Map(location=[longi,lat], zoom_start=5)
            marker = g.Marker([longi, lat], icon=g.Icon(color='blue'))
            marker.add_to(g_map)

        g_map.save('templates/map.html')

        time.sleep(1)  # delay for 1 second

@app.route("/")
def home():
    return render_template('map.html')

if __name__ == "__main__":
    threading.Thread(target=update_markers).start()
    app.run(debug=True)