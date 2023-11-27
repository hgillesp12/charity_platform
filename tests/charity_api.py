import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def check_charity_reg_number(number):
  url = "https://api.charitycommission.gov.uk/register/api/charityRegNumber/" + str(number) + "/0"
  headers = {"Ocp-Apim-Subscription-Key":API_KEY}

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

number = 1053992
get_charity_info(number)
number = 123
get_charity_info(number)
