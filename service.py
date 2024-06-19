from flask import Flask, request, render_template, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
import os
import re
from threading import Thread
import time

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("Missing Twilio Account SID or Auth Token")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

progress = {"current": 0, "total": 0, "result": []}

def parse_numbers(numbers_str):
    raw_numbers = re.split(r'[\s,]+', numbers_str.strip())
    return [num for num in raw_numbers if num]

def fetch_service_provider(number):
    formatted_number = '+91' + number.strip() if not number.strip().startswith('+91') else number.strip()
    try:
        lookup = client.lookups.phone_numbers(formatted_number).fetch(type=['carrier'])
        carrier_name = lookup.carrier.get('name', 'Unknown')
        if ' - ' in carrier_name:
            provider, circle = carrier_name.split(' - ', 1)
        else:
            provider = carrier_name
            circle = 'Unknown'
        return (formatted_number, provider, circle)
    except Exception as e:
        return (formatted_number, "Unable to fetch service provider", f"Error: {str(e)}")

def process_numbers(numbers):
    global progress
    progress["current"] = 0
    progress["total"] = len(numbers)
    progress["result"] = []
    for number in numbers:
        result = fetch_service_provider(number)
        progress["result"].append(result)
        progress["current"] += 1
        time.sleep(0.5)  # Simulate delay
    progress["result"].sort(key=lambda x: x[1])  # Sort by service provider

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numbers = request.form["numbers"].strip()
        if not numbers:
            return render_template("index.html", result=[], message="Please enter phone numbers in the input section.")
        raw_numbers = parse_numbers(numbers)
        thread = Thread(target=process_numbers, args=(raw_numbers,))
        thread.start()
        return render_template("index.html", result=[], message="Processing started. Please wait...")
    return render_template("index.html", result=[])

@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)

if __name__ == "__main__":
    app.run(debug=True)
