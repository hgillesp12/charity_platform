from flask import Flask, render_template, request  # , send_from_directory
import requests
# import os
# import matplotlib.pyplot as plt

app = Flask(__name__)

# Use API_KEY when deploying
# API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")


@app.route('/')
def default_home():
    return render_template("index.html")


@app.route('/register')
def send_to_register():
    return render_template("register.html",
                           message="Enter charity registration number")


def check_charity_reg_number(number):
    url = "https://api.charitycommission.gov.uk/register/api/"\
        "charityRegNumber/" + str(number) + "/0"
    headers = {"Ocp-Apim-Subscription-Key": "fab8692f07914991bbf31d3240b90c50"}

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


@app.route('/schedule', methods=["POST"])
def schedule_submit():
    # name=name
    day = request.form.get("day")
    time = request.form.get("time")
    location = request.form.get("location")

    if day and time and location:
        # add day, time, location to db using test_database.py functions
        if 'submit' in request.form:
            return render_template("index.html")

        else:
            return render_template("questionnaire.html",
                                   message="Schedule successfully added. Add\
                                   another schedule.")

    else:
        return render_template("questionnaire.html",
                               message="Missing data - please fill in all \
                               fields")
