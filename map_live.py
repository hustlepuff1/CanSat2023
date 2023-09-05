from flask import Flask, render_template, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def fetch_data():
    connection = mysql.connector.connect(
        host='bifrost0602.duckdns.org',
        user='TEST',
        password='1234',
        database='CANSATDB',
        port=2024
    )
    try:
        cursor = connection.cursor()
        sql = "SELECT `lat`, `longi` FROM `SENSOR`"
        cursor.execute(sql)
        result = cursor.fetchall()
    finally:
        connection.close()

    return result


@app.route("/")
def home():
    return render_template('map.html')


@app.route("/gps_data")
def get_gps_data():
    data = fetch_data()
    gps_data = [{'LAT': row[0], 'LNG': row[1]} for row in data]
    return jsonify(gps_data)


if __name__ == "__main__":
    app.run(debug=True)
