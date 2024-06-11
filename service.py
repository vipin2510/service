from flask import Flask, request, render_template
import phonenumbers
from phonenumbers import carrier

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        numbers = request.form["numbers"].split(',')
        formatted_numbers = ['+91' + number.strip() if not number.startswith('+91') else number.strip() for number in numbers]
        output = ""
        for number in formatted_numbers:
            try:
                parsed_number = phonenumbers.parse(number, "IN")
                carrier_name = carrier.name_for_number(parsed_number, "en")
                output += f"{number}: {carrier_name}<br>"
            except phonenumbers.NumberParseException:
                output += f"{number}: Invalid phone number format.<br>"
            except Exception as e:
                output += f"{number}: Unable to fetch service provider. Error: {str(e)}<br>"
        result = output
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
