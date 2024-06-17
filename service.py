from flask import Flask, request, render_template
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("Missing Twilio Account SID or Auth Token")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        numbers = request.form["numbers"].strip().split('\n')
        formatted_numbers = ['+91' + number.strip() if not number.startswith('+91') else number.strip() for number in numbers]
        for number in formatted_numbers:
            try:
                lookup = client.lookups.phone_numbers(number).fetch(type=['carrier'])
                carrier_name = lookup.carrier.get('name', 'Unknown')
                result.append((number, carrier_name))
            except Exception as e:
                result.append((number, f"Unable to fetch service provider. Error: {str(e)}"))
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
