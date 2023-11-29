from flask import Flask, render_template, send_from_directory, request
import requests
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

#Use API_KEY when deploying
#API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")

def check_charity_reg_number(number):
  url = "https://api.charitycommission.gov.uk/register/api/charityRegNumber/" + str(number) + "/0"
  headers = {"Ocp-Apim-Subscription-Key":"fab8692f07914991bbf31d3240b90c50"}

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
                message = "Invalid registration number! Try again.")
        
        name = charity_info["charity_name"]
        return render_template("questionnaire.html",
                                name = name)

# Other useful info for profile page
# Display financial info
def get_financial_history(number):
  url = "https://api.charitycommission.gov.uk/register/api/charityoverview/" + str(number) + "/0"
  headers = {"Ocp-Apim-Subscription-Key":"fab8692f07914991bbf31d3240b90c50"}

  response = requests.get(url, headers=headers)

  if response.status_code == 200:
        financial_info = response.json()
        report_year = financial_info["latest_acc_fin_year_end_date"]
        total_inc = financial_info["latest_income"]
        total_exp = financial_info["latest_expenditure"]

        inc_breakdown = {"Donations and legacies" : financial_info["inc_donations_legacies"],
        "Charitable activities" : financial_info["inc_charitable_activities"],
        "Other trading activities" : financial_info["inc_other_trading_activities"],
        "Investments" : financial_info["inc_investments"],
        "Other" : financial_info["inc_other"]}
        exp_breakdown = {"Raising funds" : financial_info["exp_raising_funds"],
        "Charitable activities" :  financial_info["exp_charitable_activities"],
        "Other" : financial_info["exp_other"]}

        inc_labels = list(inc_breakdown.keys())
        inc_values = list(inc_breakdown.values())

        exp_labels = list(exp_breakdown.keys())
        exp_values = list(exp_breakdown.values())
        
        print(report_year + ": total income = " + str(total_inc) + ". Total expenditure = " + str(total_exp))
        income_pie = plt.pie(inc_values, labels=inc_labels)
        plt.show()
        exp_pie = plt.pie(exp_values, labels=exp_labels)
        plt.show()

  else:
        return None

# Display charity description
def get_charity_overview(number):
  url = "https://api.charitycommission.gov.uk/register/api/charityoverview/" + str(number) + "/0"
  headers = {"Ocp-Apim-Subscription-Key":"fab8692f07914991bbf31d3240b90c50"}

  response = requests.get(url, headers=headers)

  if response.status_code == 200:
        overview = response.json()
        description = overview["activities"]
        print(description)

  else:
        return None

# Test code remotely
number = 1053992
get_charity_info(number)
get_financial_history(number)
get_charity_overview(number)

number = 123
get_charity_info(number)
