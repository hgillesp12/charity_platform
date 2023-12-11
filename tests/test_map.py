from flask import Flask
import folium
import json
import os

app = Flask(__name__)

borough_coordinates = {
    "Barking and Dagenham": {"coordinates": [51.5607, 0.1557], "popup": ""},
    "Barnet": {"coordinates": [51.6252, -0.1517], "popup": ""},
    "Bexley": {"coordinates": [51.4549, 0.1505], "popup": ""},
    "Brent": {"coordinates": [51.5588, -0.2817], "popup": ""},
    "Bromley": {"coordinates": [51.4039, 0.0198], "popup": ""},
    "Camden": {"coordinates": [51.5290, -0.1255], "popup": ""},
    "City of London": {"coordinates": [51.5155, -0.0922], "popup": ""},
    "Croydon": {"coordinates": [51.3762, -0.0982], "popup": ""},
    "Ealing": {"coordinates": [51.5130, -0.3089], "popup": ""},
    "Enfield": {"coordinates": [51.6538, -0.0799], "popup": ""},
    "Greenwich": {"coordinates": [51.4892, 0.0648], "popup": ""},
    "Hackney": {"coordinates": [51.5450, -0.0553], "popup": ""},
    "Hammersmith and Fulham": {"coordinates": [51.4920, -0.2236], "popup": ""},
    "Haringey": {"coordinates": [51.6000, -0.1119], "popup": ""},
    "Harrow": {"coordinates": [51.5898, -0.3346], "popup": ""},
    "Havering": {"coordinates": [51.5812, 0.1837], "popup": ""},
    "Hillingdon": {"coordinates": [51.5441, -0.4760], "popup": ""},
    "Hounslow": {"coordinates": [51.4746, -0.3680], "popup": ""},
    "Islington": {"coordinates": [51.5416, -0.1022], "popup": ""},
    "Kensington and Chelsea": {"coordinates": [51.5020, -0.1870], "popup": ""},
    "Kingston upon Thames": {"coordinates": [51.4085, -0.3064], "popup": ""},
    "Lambeth": {"coordinates": [51.5013, -0.1173], "popup": ""},
    "Lewisham": {"coordinates": [51.4452, -0.0209], "popup": ""},
    "Merton": {"coordinates": [51.4098, -0.2108], "popup": ""},
    "Newham": {"coordinates": [51.5077, 0.0469], "popup": ""},
    "Redbridge": {"coordinates": [51.5590, 0.0741], "popup": ""},
    "Richmond upon Thames": {"coordinates": [51.4479, -0.3260], "popup": ""},
    "Southwark": {"coordinates": [51.4834, -0.0821], "popup": ""},
    "Sutton": {"coordinates": [51.3618, -0.1945], "popup": ""},
    "Tower Hamlets": {"coordinates": [51.5099, -0.0059], "popup": ""},
    "Waltham Forest": {"coordinates": [51.5908, -0.0134], "popup": ""},
    "Wandsworth": {"coordinates": [51.4560, -0.1921], "popup": ""},
    "Westminster": {"coordinates": [51.4973, -0.1372], "popup": ""}
}

# Dictionary to map days to numerical values for sorting
days_mapping = {
    'Monday': 1,
    'Tuesday': 2,
    'Wednesday': 3,
    'Thursday': 4,
    'Friday': 5,
    'Saturday': 6,
    'Sunday': 7
}

# Dictionary to map times to numerical values for sorting
times_mapping = {
    'Morning': 1,
    'Afternoon': 2,
    'Evening': 3
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
        '@schema_name@', SCHEMA_NAME), [312, 'Wednesday', 'Evening', 'Camden']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [312, 'Thursday', 'Evening', 'Camden']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Wednesday', 'Afternoon', 'Ealing']
    )
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'schedule'
    ))
    rec = curs.fetchall()



    # Create a base map centered around London
    map_center = [51.509865, -0.118092]  # Coordinates for central London
    my_map = folium.Map(location=map_center, zoom_start=11)

    # Track locations with events
    locations_with_events = set()


    for schedule in rec:
        charity = schedule[1]
        day = schedule[2]
        time = schedule[3]
        location = schedule[4]
        popup_content = f"Charity: {charity}<br>Day: {day}<br>Time: {time}<br>Location: {location}"

        # Add information to the respective borough
        if location in borough_coordinates:
            locations_with_events.add(location)
            if 'popup' not in borough_coordinates[location]:
                borough_coordinates[location]['popup'] = popup_content
            else:
                borough_coordinates[location]['popup'] += f"<br><br>{popup_content}"

    # Get the absolute path to the GeoJSON file
    geojson_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'london_boroughs.geojson'))

    # Load the GeoJSON file with London borough boundaries
    with open(geojson_path, "r") as geojson_file:
        borough_geojson = json.load(geojson_file)

    # Add GeoJSON data with on-click popups
    folium.GeoJson(
        borough_geojson,
        name='geojson',
        style_function=lambda x: {
            'fillColor': 'lightblue',
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.25,
            'clickable': False  # Add this line to disable click on boroughs

        },
        highlight_function=lambda x: {
            'fillColor': 'blue',
            'color': 'blue',
            'weight': 3,
            'fillOpacity': 0.40
        },
        #tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Borough'])
    ).add_to(my_map)


    # Add event information to boroughs
    for location, data in borough_coordinates.items():
        if location in locations_with_events and data['popup']:
            # Create an HTML table string for the popup
            table_content = """
            <table style="width:100%; border-collapse: collapse; margin-top: 15px;">
                <tr>
                    <th colspan="4" style="text-align: center; font-size: 16px; padding-bottom: 10px; background-color: #FFFFFF;">{}</th>
                </tr>
                <tr>
                    <th style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">Charity</th>
                    <th style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">Day</th>
                    <th style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">Time</th>
                    <th style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">Location</th>
                </tr>
            """.format(location)

            sorted_events = sorted([schedule for schedule in rec if schedule[4] == location],
                                key=lambda x: (days_mapping[x[2]], times_mapping[x[3]]))

            for index, schedule in enumerate(sorted_events):
                background_color = "#ffffff" if index % 2 == 0 else "#f2f2f2"

                table_content += f"""
                <tr style="background-color: {background_color};">
                    <td style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">{schedule[1]}</td>
                    <td style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">{schedule[2]}</td>
                    <td style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">{schedule[3]}</td>
                    <td style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">{schedule[4]}</td>
                </tr>
                """

            table_content += "</table>"

            # Add marker only if there are events for the location
            folium.Marker(
                location=data['coordinates'],
                popup=folium.Popup(html=table_content, max_width=400),
                icon=folium.Icon(color="green", icon="glyphicon-cutlery")
            ).add_to(my_map)

    # Get the map HTML as a string
    map_html_string = my_map._repr_html_()

    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Specify the file path in the same directory as the script
    html_file_path = os.path.join(current_directory, "output.html")

    # Write the HTML content to the file
    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(map_html_string)

    assert(map_html_string)