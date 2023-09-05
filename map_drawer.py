import folium
import pandas as pd


def draw_gps_path(csv_file):
    # Read GPS data from CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Calculate the center as the mean of all Latitudes and Longitudes
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()

    # Create a Folium map centered on the calculated center
    map_center = [center_lat, center_lon]
    m = folium.Map(location=map_center, zoom_start=15)

    # Draw a path on the map using the GPS data
    folium.PolyLine(
        locations=df[['Latitude', 'Longitude']].values, color='blue').add_to(m)

    # Add a ping on the last GPS point
    last_gps_point = [df['Latitude'].iloc[-1], df['Longitude'].iloc[-1]]
    folium.Marker(location=last_gps_point, popup='Last Location',
                  icon=folium.Icon(color='green')).add_to(m)

    # Save the map to an HTML file
    m.save("gps_map.html")


if __name__ == "__main__":
    csv_file_path = "path_to_your_gps_data.csv"
    draw_gps_path(csv_file_path)
