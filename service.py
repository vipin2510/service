from flask import Flask, request, render_template, jsonify
import re
from threading import Thread
import time
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

progress = {"current": 0, "total": 0, "result": []}

def parse_numbers(numbers_str):
    raw_numbers = re.split(r'[\s,]+', numbers_str.strip())
    return [num for num in raw_numbers if num]

def get_operator(phone_number):
    phone_number = phone_number[-10:]
    url = f"https://digitalapiproxy.paytm.com/v1/mobile/getopcirclebyrange?channel=web&version=2&number={phone_number}&child_site_id=1&site_id=1&locale=en-in"
    try:
        response = requests.get(url)
        data = response.json()
        if data and 'Operator' in data:
            return (f'+91{phone_number}', data['Operator'])
        else:
            return (f'+91{phone_number}', "Unable to fetch operator information")
    except requests.RequestException as e:
        return (f'+91{phone_number}', f"Error: {str(e)}")

def process_numbers(numbers):
    global progress
    progress["current"] = 0
    progress["total"] = len(numbers)
    progress["result"] = []
    for number in numbers:
        result = get_operator(number)
        progress["result"].append(result)
        progress["current"] += 1
        time.sleep(0.5)  # Simulate delay
    progress["result"].sort(key=lambda x: x[1])  # Sort by service provider

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numbers = request.form["numbers"].strip()
        if not numbers:
            return jsonify({"message": "Please enter phone numbers in the input section."})
        raw_numbers = parse_numbers(numbers)
        thread = Thread(target=process_numbers, args=(raw_numbers,))
        thread.start()
        return jsonify({"message": "Processing started. Please wait..."})
    return render_template("index.html")

@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)

if __name__ == "__main__":
    app.run(debug=True)
