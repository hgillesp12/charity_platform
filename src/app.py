from flask import Flask, render_template, request  # , send_from_directory
import requests
# import os
# import matplotlib.pyplot as plt

app = Flask(__name__)

# Use API_KEY when deploying
# API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")


def check_charity_reg_number(number):
    url = "https://api.charitycommission.gov.uk/register/api/\
        charityRegNumber/" + str(number) + "/0"
    headers = {"Ocp-Apim-Subscription-Key": "fab8692f07914991bbf31d3240b90c50"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response

    else:
        return None


def get_charity_info(number):
    response = check_charity_reg_number(number)
    if response:
        charity_info = response.json()
        print("Hello " + charity_info["charity_name"])

    else:
        print("Invalid registration number! Try again.")


@app.route('/')
def default_home():
    return render_template("index.html")


@app.route('/register')
def send_to_register():
    return render_template("register.html",
                           message="Enter charity registration number")


@app.route('/registration_submit', methods=["POST"])
def reg_number_submit():
    reg_number = request.form.get("reg_number")
    charity_info = check_charity_reg_number(reg_number)

    if charity_info is None:
        return render_template("register.html",
                               message="Invalid registration number!\
                               Try again.")

    name = charity_info["charity_name"]
    return render_template("questionnaire.html",
                           name=name)
