from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import mysql.connector
import pandas as pd
import eventlet
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
thread = None


def background_thread():
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
            sql = "SELECT `longi`, `lat` FROM `SENSOR`"
            cursor.execute(sql)
            result = cursor.fetchall()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            connection.close()

        df = pd.DataFrame(result, columns=['longi', 'lat'])
        socketio.emit('newdata', {'data': df.to_dict(orient='records')}, namespace='/test')
        time.sleep(1)


@app.route("/")
def home():
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    print("client connected!")
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)


if __name__ == "__main__":
    socketio.run(app, debug=True)