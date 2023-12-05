import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("REGISTERED_CHARITIES_API_KEY")

number = 1053992
url = "https://api.charitycommission.gov.uk/register/api/charityRegNumber/" \
      + str(number) + "/0"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}


def test_status_code_equals_200():
   response = requests.get(url, headers=headers)
   assert response.status_code == 200


def test_response_json_format():
   response = requests.get(url, headers=headers)
   assert response.headers["Content-Type"].startswith("application/json")


def test_check_valid_name():
   response = requests.get(url, headers=headers)
   charity_info = response.json()
   name = charity_info["charity_name"]
   assert name == "ST VINCENT DE PAUL SOCIETY (ENGLAND AND WALES)"
