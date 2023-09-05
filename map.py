import mysql.connector
import folium
import pandas as pd

# Establish a connection to the database
connection = mysql.connector.connect(
    host='bifrost0602.duckdns.org',
    user='TEST',
    password='1234',
    database='CANSATDB',
    port=2024
)

try:
    cursor = connection.cursor()
    # Fetch the data from the database
    sql = "SELECT `longi`, `lat` FROM `SENSOR`"
    cursor.execute(sql)
    result = cursor.fetchall()
    print('sql connected')
finally:
    connection.close()

# Convert to pandas DataFrame for easier handling
df = pd.DataFrame(result, columns=['longi', 'lat'])

# Create a map centered at the average coordinates
average_lat, average_long = df['lat'].mean(), df['longi'].mean()
m = folium.Map(location=[average_lat, average_long])

# Add points to the map
for _, row in df.iterrows():
    folium.Marker(location=[row['lat'], row['longi']]).add_to(m)

# Save it to a file
m.save('map.html')
