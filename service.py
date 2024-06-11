from flask import Flask, request, render_template_string
import phonenumbers
from phonenumbers import carrier

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def indverex():

    if request.method == "GET":
        return "hello"

    elif request.method == "POST":
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
        return render_template_string(TEMPLATE, result=output)
    return render_template_string(TEMPLATE, result="")

TEMPLATE = '''
<!doctype html>
<html>
<head>
    <title>Service Provider Lookup</title>
</head>
<body>
    <h1>Service Provider Lookup</h1>
    <form method="post">
        <label for="numbers">Enter comma-separated numbers:</label><br>
        <input type="text" id="numbers" name="numbers" style="width: 50%;"><br><br>
        <input type="submit" value="Search">
    </form>
    <h2>Service Provider Details:</h2>
    <p>{{ result|safe }}</p>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
