from flask import Flask, render_template, request  # , send_from_directory
import requests
import os
from connection import connect_to_database

API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")

app = Flask(__name__)
SCHEMA_NAME = 'test_live_schema'

with app.app_context():
    (curs, config, conn) = connect_to_database
    # Check if the live_schema exists, if not then make it
    curs.execute(config['check_exists']['schema'].replace('@schema_name@', SCHEMA_NAME))
    rec = curs.fetchall()
    if (len(rec) == 0):
        curs.execute(config['create_schema']['new_schema'].replace('@schema_name@', SCHEMA_NAME))
        conn.commit()
    
    # Check if the three tables we need exist, if not create them
    curs.execute(config['check_exists']['table'].replace('@schema_name@', SCHEMA_NAME).replace('@table_name@', 'charity'))
    rec = curs.fetchall()
    if (len(rec) == 0):
        curs.execute(config['create_table']['charity_table'].replace('@schema_name@', SCHEMA_NAME))
        conn.commit()

    curs.execute(config['check_exists']['table'].replace('@schema_name@', SCHEMA_NAME).replace('@table_name@', 'schedule'))
    rec = curs.fetchall()
    if (len(rec) == 0):
        curs.execute(config['create_table']['schedule_table'].replace('@schema_name@', SCHEMA_NAME)) 
        conn.commit()

    curs.execute(config['check_exists']['table'].replace('@schema_name@', SCHEMA_NAME).replace('@table_name@', 'message'))
    rec = curs.fetchall()
    if (len(rec) == 0):
        curs.execute(config['create_table']['message_table'].replace('@schema_name@', SCHEMA_NAME))
        conn.commit()

@app.route('/')
def default_home():
    return render_template("index.html")


@app.route('/main')
def send_to_main():
    return render_template("main_page.html")


@app.route('/post')
def send_to_post():
    return render_template("post_message.html")


@app.route('/profile')
def send_to_profile():
    return render_template("profile_page.html")


@app.route('/register')
def send_to_register():
    return render_template("register.html",
                           message="Enter charity registration number")


def check_charity_reg_number(number):
    url = "https://api.charitycommission.gov.uk/register/api/"\
        "charityRegNumber/" + str(number) + "/0"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response

    else:
        return None


@app.route('/registration_submit', methods=["POST"])
def reg_number_submit():
    reg_number = request.form.get("reg_number")
    response = check_charity_reg_number(reg_number)

    if response:
        charity_info = response.json()
        name = charity_info["charity_name"].title()

        # add charity to db using test_database.py functions
        # parameters: reg_number and name
        return render_template("questionnaire.html",
                               name=name)

    return render_template("register.html",
                           message="Invalid registration number! \
                           Try again.")


@app.route('/schedule_submit', methods=["POST"])
def schedule_submit():
    # name=name
    day = request.form.get("day")
    time = request.form.get("time")
    location = request.form.get("location")

    if day and time and location:
        # add day, time, location to db using test_database.py functions
        if 'submit' in request.form:
            return render_template("main_page.html")

        else:
            return render_template("questionnaire.html",
                                   message="Schedule successfully added. Add\
                                   another schedule.")

    else:
        return render_template("questionnaire.html",
                               message="Missing data - please fill in all \
                               fields")
