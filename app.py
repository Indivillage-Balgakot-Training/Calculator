from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression')

    print(f"Received expression: {expression}")  # Debugging line

    try:
        # Validate the input expression to only allow numbers and basic arithmetic operations
        if not isinstance(expression, str) or not re.match(r'^[0-9\s+\-*/.()]*$', expression):
            return jsonify({"error": "Invalid expression format"}), 400

        # Safely evaluate the expression
        result = eval(expression)

        return jsonify({"result": result})

    except ZeroDivisionError:
        return jsonify({"error": "Cannot divide by zero"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
