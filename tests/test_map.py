from flask import Flask, render_template
import folium
import json
import psycopg2


app = Flask(__name__)

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

SCHEMA_NAME = "test_schema"

# Function to establish a database connection
def test_inserting_multiple_items_into_schedule_table_to_the_map(connect_to_database, create_schedule_table):
    (curs, config) = connect_to_database
    # Set up charity table with multiple entities
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP', 123]
    )
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['Feed', 312]
    )
    # Insert four entries into schedule table and assert presence
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Monday', 'Afternoon', 'Kensington and Chelsea']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Wednesday', 'Morning', 'Camden']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [312, 'Wednesday', 'Morning', 'Hackney']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [312, 'Tuesday', 'Evening', 'Camden']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Wednesday', 'Afternoon', 'Ealing']
    )
     curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'schedule'
    ))
    rec = curs.fetchall()


    for schedule in rec:
        charity = schedule[0]
        day = schedule[1]
        time = schedule[2]
        location = schedule[3]
        popup_content = f"Charity: {charity}<br>Day: {day}<br>Time: {time}<br>Location: {location}"
            folium.Marker(
                location = borough_coordinates[location], # Replace with actual coordinates based on location
                popup=popup_content,
                icon=folium.Icon(color="green", icon="calendar")
            ).add_to(my_map)

    # Create a dictionary to store the borough coordinates
    


    # Create a base map centered around London
    map_center = [51.509865, -0.118092]  # Coordinates for central London
    my_map = folium.Map(location=map_center, zoom_start=11)

    # Iterate over the fetched schedule data and add markers to the map
    for entry in schedule_data:
        charity, day, time, location = entry
        # Customize the popup content based on your requirements
        popup_content = f"Charity: {charity}<br>Day: {day}<br>Time: {time}<br>Location: {location}"

        # Add a marker to the map
        folium.Marker(
            location=[51.509865, -0.118092],  # Replace with actual coordinates based on location
            popup=popup_content,
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
    return render_template("test_main_page.html", map_html_string=map_html_string)

    