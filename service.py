from flask import Flask, request, render_template
from twilio.rest import Client
import os

app = Flask(__name__)

# Twilio credentials
# It's better to use environment variables for credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC5cc1200a3f9f178a7464da21d62725fc')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'eb06dd8e45b2e3c54c3b21df3d05db5a')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        numbers = request.form["numbers"].split(',')
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
