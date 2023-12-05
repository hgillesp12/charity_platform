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
        "Barking and Dagenham": [51.5607, 0.1557],
        "Barnet": [51.6252, -0.1517],
        "Bexley": [51.4549, 0.1505],
        "Brent": [51.5588, -0.2817],
        "Bromley": [51.4039, 0.0198],
        "Camden": [51.5290, -0.1255],
        "Ealing": [51.5130, -0.3089],
        "Enfield": [51.6538, -0.0799],
        "Greenwich": [51.4892, 0.0648],
        "Hackney": [51.5450, -0.0553],
        "Hammersmith and Fulham": [51.4920, -0.2236],
        "Haringey": [51.6000, -0.1119],
        "Harrow": [51.5898, -0.3346],
        "Havering": [51.5812, 0.1837],
        "Hillingdon": [51.5441, -0.4760],
        "Hounslow": [51.4746, -0.3680],
        "Islington": [51.5416, -0.1022],
        "Kensington and Chelsea": [51.5020, -0.1870],
        "Kingston upon Thames": [51.4085, -0.3064],
        "Lambeth": [51.5013, -0.1173],
        "Merton": [51.4098, -0.2108],
        "Newham": [51.5077, 0.0469],
        "Redbridge": [51.5590, 0.0741],
        "Richmond upon Thames": [51.4479, -0.3260],
        "Sutton": [51.3618, -0.1945],
        "Tower Hamlets": [51.5099, -0.0059],
        "Waltham Forest": [51.5908, -0.0134],
        "Wandsworth": [51.4560, -0.1921],
        "Westminster": [51.4973, -0.1372]
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

