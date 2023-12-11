from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import unquote
import string
import requests
import os
import folium
import json
from datetime import datetime
import configparser
import psycopg2 as db
import logging

app = Flask(__name__)

SCHEMA_NAME = 'test__schema'
API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")
logging.basicConfig(level=logging.INFO)


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

def connect_to_database():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, 'dbtool.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    conn = db.connect(dbname=os.getenv('DB_NAME'),
                      user=os.getenv('DB_USER'),
                      password=os.getenv('DB_PASSWORD'),
                      host=os.getenv('DB_HOST'),
                      port=os.getenv('DB_PORT'),
                      client_encoding=os.getenv('DB_CLIENT_ENCODING'))
    logging.info("Connected to database")
    curs = conn.cursor()
    return curs, config, conn


with app.app_context():
    (curs, config, conn) = connect_to_database()

    # Function to create the schema if it does not yet exist
    def create_schema():
        try:
            curs.execute(config['create_schema']['new_schema'].replace
                         ('@schema_name@', SCHEMA_NAME))
            conn.commit()
        except Exception as e:
            logging.info(e)
            conn.rollback()

    # Function to create table (or type) if not exists
    def create_table(create_table_query):
        try:
            curs.execute(create_table_query.replace
                         ('@schema_name@', SCHEMA_NAME))
            conn.commit()
        except Exception as e:
            logging.info(e)
            conn.rollback()

    # Check and create schema
    create_schema()

    # Check and create tables
    create_table(config['create_table']['charity_table'])
    create_table(config['create_table']['day_enum'])
    create_table(config['create_table']['time_enum'])
    create_table(config['create_table']['schedule_table'])
    create_table(config['create_table']['message_table'])

    conn.close()


@app.route('/')
def send_to_register():
    return render_template("register.html",
                           message="Login with your charity registration \
                            number")


@app.route('/about')
def send_to_about():
    return render_template("about.html")


@app.route('/post_message/<name>/<reg_number>')
def post_new_message(name, reg_number):
    return render_template("post_message.html",
                           name=name,
                           reg_number=reg_number,
                           content="Post a new message!")


def check_charity_reg_number(number):
    url = "https://api.charitycommission.gov.uk/register/api/"\
        "charityRegNumber/" + str(number) + "/0"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response
    else:
        return None


def get_all_registered_charities():
    all_charities = []
    (curs, config, conn) = connect_to_database()
    try:
        curs.execute(config['query']['select_all_registered_charities'].replace(
            '@schema_name@', SCHEMA_NAME))
        rec = curs.fetchall()
        conn.close()
        for charity in rec:
            all_charities.append(charity[0])
        return all_charities
    except Exception as c:
        logging.info(c)
        conn.rollback()
        conn.close()


@app.route('/login_submit', methods=["POST"])
def send_to_profile_page():
    reg_number = request.form.get("reg_number")
    response = check_charity_reg_number(reg_number)
    if not response:
        return render_template("register.html",
                               message="Invalid charity ID number! \
                                Try again.")
    charity_info = response.json()
    name = string.capwords(charity_info["charity_name"])

    register_first = "Registration not found - please register first"

    # add check to make sure the charity logging in is already registered
    curs, config, conn = connect_to_database()
    try:
        # Check if the charity is already in the database first
        curs.execute(config['query']['select_charity_by_number'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number]
        )
        if (curs.rowcount == 1):
            conn.close()
            logging.info("Charity %s successfully logged in", reg_number)
            charities = get_all_registered_charities()
            all_messages = get_all_messages()
            schedule = get_schedules_by_charity(reg_number)
            map_html_string = generate_map()
            return render_template("main_page.html", 
                                    name=name,
                                    reg_number=reg_number,
                                    all_messages=json.loads(all_messages),
                                    map_html_string=map_html_string,
                                    days=days_mapping,
                                    times=times_mapping,
                                    locations=borough_coordinates,
                                    charities=charities,
                                    schedule=json.loads(schedule)
                                    )
        else:
            conn.close()
            logging.info("Charity %s tried to log in but is not yet \
                         registered", reg_number)
            return render_template("register.html",
                                   message=register_first)
    except Exception as e:
        logging.error(e)
        conn.rollback
        conn.close()
        return render_template("register.html", message=register_first)


@app.route('/registration_submit', methods=["POST"])
def reg_number_submit():
    reg_number = request.form.get("reg_number")
    response = check_charity_reg_number(reg_number)

    invalid_message = "Invalid registration number - please try again"
    already_registerd = "Your charity is already registered - please log in"
    unknown_error = "Unkown error - please try again"

    if not response:
        logging.info("Received invalid registration number %s", reg_number)
        return render_template("register.html", message=invalid_message)

    try:
        charity_info = response.json()
        name = string.capwords(charity_info["charity_name"])
    except Exception as e:
        logging.error(e)

    # Add charity to the charity table
    # Parameters: reg_number and name
    curs, config, conn = connect_to_database()
    try:
        # Check if the charity is already in the database first
        curs.execute(config['query']['select_charity_by_number'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number]
        )
        if (curs.rowcount == 1):
            conn.close()
            logging.info("Charity %s is already registered", reg_number)
            return render_template("register.html", message=already_registerd)
    except Exception as e:
        logging.error(e)
        conn.rollback
        conn.close()
        return render_template("register.html", message=unknown_error)

    # charity is not in the database, so add it
    try:
        curs.execute(config['insert_into']['charity_table'].replace(
            '@schema_name@', SCHEMA_NAME), [name, reg_number]
        )
        if curs.rowcount == 1:
            conn.commit()
            conn.close()
            logging.info("Added charity %s %s to the database", name,
                         reg_number)
            return render_template("questionnaire.html",
                                   name=name,
                                   reg_number=reg_number,
                                   message="Please complete the following \
                                    form")
        else:
            conn.close()
            logging.error("Unable to add %s %s to the database", name,
                          reg_number)
            return render_template("register.html", message=invalid_message)
    except Exception as e:
        conn.rollback
        conn.close()
        logging.error(e)
        return render_template("register.html", message=unknown_error)


@app.route('/questionnaire/<name>/<reg_number>')
def submit_new_schedule(name, reg_number):
    return render_template("questionnaire.html",
                           name=name,
                           reg_number=reg_number,
                           message="Submit a new schedule")


@app.route('/main/<name>/<reg_number>')
def back_home(name, reg_number):
    charities = get_all_registered_charities()
    all_messages = get_all_messages()
    map_html_string = generate_map()
    schedule = get_schedules_by_charity(reg_number)
    return render_template("main_page.html",
                           name=name,
                           reg_number=reg_number,
                           all_messages=json.loads(all_messages),
                           map_html_string=map_html_string,
                           schedule=json.loads(schedule),
                            days=days_mapping,
                            times=times_mapping,
                            locations=borough_coordinates,
                            charities=charities
                           )


def get_all_messages():
    (curs, config, conn) = connect_to_database()
    message_table = {
        "sender_number": [],
        "sender_name": [],
        "content": [],
        "date_time": []
    }
    try:
        curs.execute(config['query']
                     ['select_all_message_with_names_order_by_timestamp_desc'].
                     replace('@schema_name@', SCHEMA_NAME))
        all_messages = curs.fetchall()
        for message_info in all_messages:
            message_table["sender_number"].append(message_info[1])
            message_table["sender_name"].append(message_info[4])
            message_table["content"].append(message_info[2])
            message_table["date_time"].append(message_info[3].strftime("%d/%m/%Y, %H:%M:%S"))
        conn.close()
        message_json=json.dumps(message_table, indent = 4)
        return message_json
    except Exception as e:
        logging.info(e)
        conn.rollback() 
        conn.close()


@app.route('/schedule_submit/<name>/<reg_number>', methods=['POST'])
def schedule_submit(name, reg_number):
    day = request.form.get("day")
    time = request.form.get("time")
    location = request.form.get("location")

    missing_data = "Missing data - please fill in all fields"
    not_added_correct = "Schedule not added - please try again"
    successful_add = "Schedule added"

    if not (day and time and location):
        logging.info("Missing data in schedule submission: %s, %s, %s",
                     day, time, location)
        return render_template("questionnaire.html", 
                               name=name, 
                               reg_number=reg_number,
                               message=missing_data)
    
    logging.info("Received request to save schedule with %s, %s, and %s", day, time, location)
    
    curs, config, conn = connect_to_database()
    try:
        curs.execute(config['insert_into']['schedule_table'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number, day, time, location]
        )
        if curs.rowcount == 1:
            conn.commit()
            conn.close()
            logging.info("Added schedule %s, %s, %s, %s to the database", reg_number, day, time, location)
            return render_template("questionnaire.html", 
                        name=name, 
                        reg_number=reg_number, 
                        message=successful_add)
        else:
            conn.close()
            logging.info("Unable to add schedule %s, %s, %s, %s to the database", reg_number, day, time, location)
            return render_template("questionnaire.html", 
                                   name=name, 
                                   reg_number=reg_number, 
                                   message=not_added_correct)
    except Exception as e:
        conn.rollback
        conn.close()
        logging.error(e)
        return render_template("questionnaire.html", 
                               name=name, 
                               reg_number=reg_number,
                               message=not_added_correct)
    

@app.route('/post_message/<name>/<reg_number>', methods=["POST"])
def post_message(name, reg_number):
    message = request.form.get("message")
    now = datetime.now()
    sql_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    add_message = "Add a message to post."
    error_message = "Message could not be posted."

    if 'cancel' in request.form:
        charities = get_all_registered_charities()
        all_messages = get_all_messages()
        schedule = get_schedules_by_charity(reg_number)
        map_html_string = generate_map()
        return render_template("main_page.html", 
                                name=name,
                                reg_number=reg_number,
                                all_messages=json.loads(all_messages),
                                map_html_string=map_html_string,
                                schedule=json.loads(schedule),
                                days=days_mapping,
                                times=times_mapping,
                                locations=borough_coordinates,
                                charities=charities
                                )

    if not message:
        logging.info("Missing message content")
        return render_template("post_message.html",
                               name=name,
                               reg_number=reg_number,
                               content=add_message)
    
    logging.info("Received request to save new message from %s", reg_number)

    curs, config, conn = connect_to_database()
    try:
        curs.execute(config['insert_into']['message_table'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number, message, sql_timestamp]
        )
        if curs.rowcount == 1:
            conn.commit()
            conn.close()
            logging.info("Added message to database")
            charities = get_all_registered_charities()
            all_messages = get_all_messages()
            schedule = get_schedules_by_charity(reg_number)
            map_html_string = generate_map()
            return render_template("main_page.html", 
                                    name=name,
                                    reg_number=reg_number,
                                    all_messages=json.loads(all_messages),
                                    map_html_string=map_html_string,
                                    schedule=json.loads(schedule),
                                    days=days_mapping,
                                    times=times_mapping,
                                    locations=borough_coordinates,
                                    charities=charities
                                    )
        else:
            conn.close()
            logging.info("Unable to add message from %s to the database", reg_number)
            return render_template("post_message.html",
                                   name=name,
                                   reg_number=reg_number, 
                                   content=error_message)
    except Exception as e:
        conn.rollback
        conn.close()
        logging.error(e)
        return render_template("post_message.html",
                               name=name,
                               reg_number=reg_number, 
                               content=error_message)


def get_schedules_by_charity(reg_number):
    (curs, config, conn) = connect_to_database() 
    
    schedule_table = {
        "id":[],
        "day": [],
        "time": [],
        "location": []
    }
    
    try:
        curs.execute(config['query']['select_schedule_by_charity_number'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number]
        )
        rec = curs.fetchall()
        for event_info in rec:
            schedule_table["id"].append(event_info[0])
            schedule_table["day"].append(event_info[2])
            schedule_table["time"].append(event_info[3])
            schedule_table["location"].append(event_info[4])        
        conn.close()
        schedule_json = json.dumps(schedule_table, indent = 4) 
        return schedule_json
    except Exception as e:
        logging.info(e)
        conn.rollback()
        conn.close()


def delete_single_event(id):
    (curs, config, conn) = connect_to_database() 
    
    try:
        curs.execute(config['delete_from']['delete_event_from_schedule'].replace(
            '@schema_name@', SCHEMA_NAME), [id]
        )
        if (curs.rowcount == 1):
            conn.commit()
        conn.close()
    except Exception as e:
        logging.info(e)
        conn.rollback()
        conn.close()


@app.route('/delete_event/<name>/<reg_number>', methods=["POST"])
def delete_event(name, reg_number):
    decoded_name = unquote(name)
    id = request.form.get("rowId")
    delete_single_event(id)
    return redirect(url_for('back_home', name=decoded_name, reg_number=reg_number))

# Can we delete this function - seems like it's not being used?
def get_all_schedules():
    (curs, config, conn) = connect_to_database()
    message_table = {
        "sender_name": [],
        "content": [],
        "date_time": []
    }
    try:
        curs.execute(config['query']['select_all_message_with_names_order_by_timestamp_desc'].replace('@schema_name@', SCHEMA_NAME))
        all_messages = curs.fetchall()
        for message_info in all_messages:
            message_table["sender_name"].append(message_info[4])
            message_table["content"].append(message_info[2])
            message_table["date_time"].append(message_info[3].strftime("%d/%m/%Y, %H:%M:%S"))
        conn.close()
        message_json = json.dumps(message_table, indent = 4) 
        return message_json
    except Exception as e:
        logging.info(e)
        conn.rollback()   
        conn.close()


@app.route('/contact_info/<original_name>/<original_reg_number>/<name>/<reg_number>')
def send_to_contact_page(original_name, original_reg_number, name, reg_number):
    response = get_charity_contact_info(reg_number)
    decoded_name = unquote(original_name)

    if response:
        charity_contact_info = response.json()
        address = charity_contact_info["contact_address"]
        phone_number = charity_contact_info["phone"]
        email = charity_contact_info["email"]
        website = charity_contact_info["web"]
        
        return render_template("contact_info.html",
                               name=name,
                               address=address,
                               phone_number=phone_number,
                               email=email,
                               website=website,
                               original_name=decoded_name,
                               original_reg_number=original_reg_number)
    else:
        return render_template("contact_info.html",
                               name=None
                               )


def get_charity_contact_info(number):
    url = "https://api.charitycommission.gov.uk/register/api/"\
        "charitycontactinformation/" + str(number) + "/0"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response
    else:
        return None@app.route('/filter_map/<name>/<reg_number>', methods=['POST'])


def filter_map(name, reg_number):
    day = request.form.get("day")
    time = request.form.get("time")
    location = request.form.get("location")
    charity = request.form.get("charity")
    logging.info("Received request to filter map by %s, %s, %s, %s", day, time, location, charity)
    charities = get_all_registered_charities()
    all_messages = get_all_messages()
    map_html_string = generate_map(day, time, location, charity)
    return render_template("main_page.html", 
                            name=name,
                            reg_number=reg_number,
                            all_messages=json.loads(all_messages),
                            map_html_string=map_html_string,
                            days=days_mapping,
                            times=times_mapping,
                            locations=borough_coordinates,
                            charities=charities,
                            selected_day=day,
                            selected_time=time,
                            selected_location=location,
                            selected_charity=charity
                            )

# Function to establish a database connection
def generate_map(day=None, time=None, location=None, charity=None):
    (curs, config, conn) = connect_to_database() 

    criteria_to_add = []
    items_to_input = []

    if day:
        criteria_to_add.append(SCHEMA_NAME + '.schedule.day=%s')
        items_to_input.append(day)
    if time:
        criteria_to_add.append(SCHEMA_NAME + '.schedule.time=%s')
        items_to_input.append(time)
    if location:
        criteria_to_add.append(SCHEMA_NAME + '.schedule.location=%s')
        items_to_input.append(location)
    if charity:
        criteria_to_add.append(SCHEMA_NAME + '.charity.name=%s')
        items_to_input.append(charity)

    criteria = ''
    for item in criteria_to_add:
        if criteria == '':
            criteria += 'WHERE ' + item
        else:
            criteria += ' AND ' + item

    try:
        curs.execute(config['query']['select_query_experiment'].replace(
            '@schema_name@', SCHEMA_NAME).replace('@criteria@', criteria), items_to_input)
        rec = curs.fetchall()
        conn.close()
        return generate_map_html(rec)
    except Exception as c:
        logging.info(c)
        conn.rollback()
        conn.close()

def generate_map_html(schedules):

    # Create a base map centered around London
    map_center = [51.509865, -0.118092]  # Coordinates for central London
    my_map = folium.Map(location=map_center, zoom_start=11)

    # Track locations with events
    locations_with_events = set()

    for schedule in schedules:
        charity = schedule[5]
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

            sorted_events = sorted([schedule for schedule in schedules if schedule[4] == location],
                                key=lambda x: (days_mapping[x[2]], times_mapping[x[3]]))

            for index, schedule in enumerate(sorted_events):
                background_color = "#ffffff" if index % 2 == 0 else "#f2f2f2"

                table_content += f"""
                <tr style="background-color: {background_color};">
                    <td style="padding: 3px; text-align: left; border-bottom: 1px solid #ddd; padding-right: 15px;">{schedule[5]}</td>
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


    return map_html_string

