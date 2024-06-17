from flask import Flask, request, render_template, flash
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("Missing Twilio Account SID or Auth Token")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def parse_numbers(numbers_str):
    # Use regex to split by commas, spaces, or line breaks
    raw_numbers = re.split(r'[\s,]+', numbers_str.strip())
    # Remove empty strings
    return [num for num in raw_numbers if num]

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        numbers = request.form["numbers"].strip()
        if not numbers:
            flash("Please enter phone numbers in the input section.")
        else:
            raw_numbers = parse_numbers(numbers)
            formatted_numbers = ['+91' + number.strip() if not number.strip().startswith('+91') else number.strip() for number in raw_numbers]
            for number in formatted_numbers:
                try:
                    lookup = client.lookups.phone_numbers(number).fetch(type=['carrier'])
                    carrier_name = lookup.carrier.get('name', 'Unknown')
                    # Split carrier_name into provider and circle
                    if ' - ' in carrier_name:
                        provider, circle = carrier_name.split(' - ', 1)
                    else:
                        provider = carrier_name
                        circle = 'Unknown'
                    result.append((number, provider, circle))
                except Exception as e:
                    result.append((number, "Unable to fetch service provider", f"Error: {str(e)}"))
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
