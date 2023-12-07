from flask import Flask, render_template, request  # , send_from_directory
import requests
import os
import json
from datetime import datetime
import configparser
import psycopg2 as db
import logging

app = Flask(__name__)

SCHEMA_NAME = 'test__schema'
API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")
logging.basicConfig(level=logging.INFO) 

def connect_to_database():
    #dirname = os.getcwd()
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
            curs.execute(config['create_schema']['new_schema'].replace('@schema_name@', SCHEMA_NAME))
            conn.commit()
        except Exception as e:
            logging.info(e)
            conn.rollback()

    # Function to create table (or type) if not exists
    def create_table(create_table_query):
        try:
            curs.execute(create_table_query.replace('@schema_name@', SCHEMA_NAME))
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
                           message="Login with your charity registration number")

@app.route('/about')
def send_to_about():
    return render_template("about.html")


@app.route('/post_message/<name>/<reg_number>')
def post_new_message(name, reg_number):
    return render_template("post_message.html", name=name, reg_number=reg_number,
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


@app.route('/login_submit', methods=["POST"])
def send_to_profile_page():
    reg_number = request.form.get("reg_number")
    response = check_charity_reg_number(reg_number)
    if not response:
        return render_template("register.html", 
                               message="Invalid charity ID number! Try again.")
    charity_info = response.json()
    name = charity_info["charity_name"].title()
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
            all_messages = get_all_messages()
            return render_template("main_page.html", 
                                    name=name,
                                    reg_number=reg_number,
                                    all_messages=json.loads(all_messages)
                                    )
        else:
            conn.close()
            logging.info("Charity %s tried to log in but is not yet registered", reg_number)
            return render_template("register.html", message=register_first)  
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
        name = charity_info["charity_name"].title()
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
            logging.info("Added charity %s %s to the database", name, reg_number)
            return render_template("questionnaire.html", 
                                   name=name, 
                                   reg_number=reg_number, 
                                   message="Please complete the following form")
        else:
            conn.close()
            logging.error("Unable to add %s %s to the database", name, reg_number)
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
    all_messages = get_all_messages()
    return render_template("main_page.html", name=name, reg_number=reg_number, all_messages=json.loads(all_messages))


def get_all_messages():
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


@app.route('/schedule_submit/<name>/<reg_number>', methods=['POST'])
def schedule_submit(name, reg_number):
    day = request.form.get("day")
    time = request.form.get("timeOfDay")
    location = request.form.get("location")

    missing_data = "Missing data - please fill in all fields"
    not_added_correct = "Schedule not added - please try again"
    successful_add = "Schedule added"

    if not (day and time and location):
        logging.info("Missing data in schedule submission: %s, %s, %s", day, time, location)
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
    
    if 'submit' in request.form:
        ### TODO: This should be refactored / reworked ### 
        all_messages = get_all_messages()
        return render_template("main_page.html", 
                               name=name, 
                               reg_number=reg_number,
                               all_messages=json.loads(all_messages))
    else:
        return render_template("questionnaire.html", 
                               name=name, 
                               reg_number=reg_number, 
                               message=successful_add)


@app.route('/post_message/<name>/<reg_number>', methods=["POST"])
def post_message(name, reg_number):
    message = request.form.get("message")
    now = datetime.now()
    sql_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    add_message = "Add a message to post."
    error_message = "Message could not be posted."

    if 'cancel' in request.form:
        all_messages = get_all_messages()
        return render_template("main_page.html",
                                name=name,
                                reg_number=reg_number,
                                all_messages=json.loads(all_messages)
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
            all_messages = get_all_messages()
            return render_template("main_page.html",
                                   name=name,
                                   reg_number=reg_number,
                                   all_messages=json.loads(all_messages)
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
