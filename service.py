from flask import Flask, request, render_template, jsonify
import re
import requests

app = Flask(__name__)

def parse_numbers(numbers_str):
    raw_numbers = re.split(r'[\s,]+', numbers_str.strip())
    return [num for num in raw_numbers if num]

def fetch_service_provider(number):
    formatted_number =  number.strip() if not number.strip().startswith('+91') else number.strip()
    url = f"https://digitalapiproxy.paytm.com/v1/mobile/getopcirclebyrange?channel=web&version=2&number={formatted_number}&child_site_id=1&site_id=1&locale=en-in"
    try:
        response = requests.get(url)
        data = response.json()
        operator = data.get('Operator', 'Unknown')
        circle = data.get('Circle', 'Unknown')
        return (formatted_number, operator, circle)
    except Exception as e:
        return (formatted_number, "Unable to fetch service provider", f"Error: {str(e)}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numbers = request.form["numbers"].strip()
        if not numbers:
            return render_template("index.html", result=[], message="Please enter phone numbers in the input section.")
        raw_numbers = parse_numbers(numbers)
        result = []
        for number in raw_numbers:
            result.append(fetch_service_provider(number))
        result.sort(key=lambda x: x[1])  # Sort by service provider
        return render_template("index.html", result=result, message="Processing complete.")
    return render_template("index.html", result=[])

if __name__ == "__main__":
    app.run(debug=True)
