from flask import Flask, request, render_template, jsonify
import os
import re
import requests
from threading import Thread
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

progress = {"current": 0, "total": 0, "result": []}

def parse_numbers(numbers_str):
    raw_numbers = re.split(r'[\s,]+', numbers_str.strip())
    return [num for num in raw_numbers if num]

def fetch_service_provider(number):
    formatted_number =  + number.strip() if not number.strip().startswith('+91') else number.strip()
    url = f"https://digitalapiproxy.paytm.com/v1/mobile/getopcirclebyrange?channel=web&version=2&number={formatted_number}&child_site_id=1&site_id=1&locale=en-in"
    try:
        response = requests.get(url)
        data = response.json()
        operator = data.get('Operator', 'Unknown')
        circle = data.get('Circle', 'Unknown')
        return (formatted_number, operator, circle)
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

if __name__ != "__main__":
    # Vercel requires the app variable to be callable in the entry point
    app = app
