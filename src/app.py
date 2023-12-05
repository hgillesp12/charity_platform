from flask import Flask, render_template
import folium
import json

app = Flask(__name__)

@app.route('/main_page')
def index():
    # Sample events and their locations in London boroughs
    events = [
        {"charity": "Charity X", "event": "Soup Kitchen X", "day": "Monday", "time": "Morning", "location": "Croydon"},
        {"charity": "Charity Y", "event": "Soup Kitchen Y", "day": "Wednesday", "time": "Afternoon", "location": "Chelsea"},
        {"charity": "Charity X", "event": "Soup Kitchen X", "day": "Wednesday", "time": "Afternoon", "location": "Chelsea"},
        {"charity": "Charity Z", "event": "Soup Kitchen Z", "day": "Wednesday", "time": "Morning", "location": "Lewisham"},
        {"charity": "Charity X", "event": "Soup Kitchen X", "day": "Friday", "time": "Morning", "location": "Southwark"},
    ]

    # Create a dictionary to store the borough coordinates
    borough_coordinates = {
        "Croydon": [51.3762, -0.0982],
        "Chelsea": [51.4876, -0.1681],
        "Lewisham": [51.4415, -0.0117],
        "Southwark": [51.4834, -0.0821],
    }

    # Create a base map centered around London
    map_center = [51.509865, -0.118092]  # Coordinates for central London
    my_map = folium.Map(location=map_center, zoom_start=11)

    # Add markers for each event
    for event in events:
        location = borough_coordinates.get(event["location"])
        if location:
            folium.Marker(
                location=location,
                popup=f"{event['charity']} - {event['event']}<br>{event['day']} {event['time']}",
                icon=folium.Icon(color="green", icon="calendar")
            ).add_to(my_map)

    # Load the GeoJSON file with London borough boundaries
    with open("../london_boroughs.geojson", "r") as geojson_file:
        borough_geojson = json.load(geojson_file)

    # Overlay borough boundaries on the map
    folium.GeoJson(borough_geojson).add_to(my_map)

    # Get the map HTML as a string
    map_html_string = my_map._repr_html_()

    # Render the main_page.html template with the map HTML string and events data
    return render_template("main_page.html", map_html_string=map_html_string, events=events)