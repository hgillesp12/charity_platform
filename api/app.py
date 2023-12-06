from flask import Flask, render_template, request  # , send_from_directory
import requests
import os
from datetime import datetime
import configparser
import psycopg2 as db

API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")
SCHEMA_NAME = 'test_schema'

app = Flask(__name__)
SCHEMA_NAME = 'test_new_schema'

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
    curs = conn.cursor()
    return curs, config, conn

with app.app_context():
    (curs, config, conn) = connect_to_database()

    # Function to check and create schema if not exists
    def create_schema():
        try:
            curs.execute(config['check_exists']['schema'], [SCHEMA_NAME])
            if curs.rowcount == 0:
                curs.execute(config['create_schema']['new_schema'].replace('@schema_name@', SCHEMA_NAME))
                conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()

    # Function to check and create a table if not exists
    def create_table(table_name, create_table_query):
        try:
            curs.execute(config['check_exists']['table'], [SCHEMA_NAME, table_name])
            if curs.rowcount == 0:
                curs.execute(create_table_query.replace('@schema_name@', SCHEMA_NAME))
                conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()

    # Check and create schema
    create_schema()

    # Check and create tables
    create_table('charity', config['create_table']['charity_table'])
    create_table('day_enum', config['create_table']['day_enum'])
    create_table('time_enum', config['create_table']['time_enum'])
    create_table('schedule_table', config['create_table']['schedule_table'])
    create_table('message', config['create_table']['message_table'])

    conn.close()


@app.route('/')
def default_home():
    return render_template("index.html")


@app.route('/main')
def send_to_main():
    return render_template("main_page.html")


@app.route('/post_message/<name>/<reg_number>')
def post_new_message(name, reg_number):
    return render_template("post_message.html", name=name, reg_number=reg_number,
                           content="Post a new message!")


@app.route('/profile')
def send_to_profile():
    return render_template("profile_page.html")


@app.route('/register')
def send_to_register():
    return render_template("register.html",
                           message="Login with your charity registration number")


def check_charity_reg_number(number):
    url = "https://api.charitycommission.gov.uk/register/api/"\
        "charityRegNumber/" + str(number) + "/0"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response

    else:
        return None

@app.route('/login')
def send_to_login():
    return render_template("login.html")

@app.route('/login_submit', methods=["POST"])
def send_to_profile_page():
    reg_number = request.form.get("reg_number")
    response = check_charity_reg_number(reg_number)
    if not response:
        return render_template("login.html", 
                               message="Invalid charity ID number! Try again.")
    charity_info = response.json()
    name = charity_info["charity_name"].title()
    return render_template("profile_page.html", name=name, reg_number=reg_number)

@app.route('/registration_submit', methods=["POST"])
def reg_number_submit():
    reg_number = request.form.get("reg_number")
    response = check_charity_reg_number(reg_number)
    
    if not response:
        return render_template("register.html", 
                               message="Invalid registration number! Try again.")

    try:
        charity_info = response.json()
        name = charity_info["charity_name"].title()

        # Add charity to the database using test_database.py functions
        # Parameters: reg_number and name
        curs, config, conn = connect_to_database()

        try:
            curs.execute(config['query']['select_charity_by_number'].replace(
                '@schema_name@', SCHEMA_NAME), [reg_number]
            )
            if (curs.rowcount == 1):
                return render_template("index.html", 
                                       message="Charity already registered. Please log in.")
        except Exception as e:
            print(f"Error: {e}")
            return render_template("register.html", 
                               message="Invalid registration number! Try again.") 

        curs.execute(config['insert_into']['charity_table'].replace(
            '@schema_name@', SCHEMA_NAME), [name, reg_number]
        )

        if curs.rowcount == 1:
            conn.commit()
            return render_template("questionnaire.html", name=name, reg_number=reg_number)
        else:
            return render_template("register.html",
                                message="Invalid registration number! Try again.")
    
    except Exception as e:
        print(f"Error: {e}")
        return render_template("register.html", 
                               message="Invalid registration number! Try again.")


@app.route('/questionnaire/<name>/<reg_number>')
def submit_new_schedule(name, reg_number):
    return render_template("questionnaire.html", name=name, reg_number=reg_number,
                           message="Submit a new schedule")

@app.route('/schedule_submit/<name>/<reg_number>', methods=['POST'])
def schedule_submit(name, reg_number):
    day = request.form.get("day")
    time = request.form.get("time")
    location = request.form.get("location")

    if not (day and time and location):
        return render_template("questionnaire.html", name=name, reg_number=reg_number,
                               message="Missing data - please fill in all \
                               fields")
    
    try:
        curs, config, conn = connect_to_database()
        curs.execute(config['insert_into']['schedule_table'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number, day, time, location]
        )
        if curs.rowcount == 1:
            conn.commit()
            if 'submit' in request.form:
                return render_template("main_page.html")
            else:
                return render_template("questionnaire.html", name=name, reg_number=reg_number, 
                                   message="Schedule successfully added. Add\
                                   another schedule.")
        else:
            return render_template("questionnaire.html", name=name, reg_number=reg_number, 
                                   message="Schedule not added successfully. Add\
                                   another schedule.")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("questionnaire.html", name=name, reg_number=reg_number,
                                   message="Schedule not added successfully. Add\
                                   another schedule.")


@app.route('/post_message/<name>/<reg_number>', methods=["POST"])
def post_message(name, reg_number):
    message = request.form.get("message")
    now = datetime.now()
    sql_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    if 'cancel' in request.form:
        return render_template("profile_page.html",
                               name=name,
                               reg_number=reg_number)

    if not message:
        return render_template("post_message.html",
                               name=name,
                               reg_number=reg_number,
                               content="Add a message to post.")
    
    try:
        curs, config, conn = connect_to_database()
        curs.execute(config['insert_into']['message_table'].replace(
            '@schema_name@', SCHEMA_NAME), [reg_number, message, sql_timestamp]
        )
        if curs.rowcount == 1:
            conn.commit()
            return render_template("profile_page.html",
                                   name=name,
                                   reg_number=reg_number)
        else:
            return render_template("post_message.html",
                                   name=name,
                                   reg_number=reg_number, 
                                   content="Message could not be posted.")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("post_message.html",
                               name=name,
                               reg_number=reg_number, 
                               content="Message could not be posted.")
