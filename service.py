from flask import Flask, request, render_template
import phonenumbers
from phonenumbers import carrier

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = []
    if request.method == "POST":
        numbers = request.form["numbers"].split(',')
        formatted_numbers = ['+91' + number.strip() if not number.startswith('+91') else number.strip() for number in numbers]
        for number in formatted_numbers:
            try:
                parsed_number = phonenumbers.parse(number, "IN")
                carrier_name = carrier.name_for_number(parsed_number, "en")
                result.append((number, carrier_name))
            except phonenumbers.NumberParseException:
                result.append((number, "Invalid phone number format"))
            except Exception as e:
                result.append((number, f"Unable to fetch service provider. Error: {str(e)}"))
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
