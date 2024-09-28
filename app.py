from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def evaluate_expression(expression):
    try:
        # Replace 'x²' with '**2' and 'x³' with '**3'
        expression = expression.replace('x²', '**2').replace('x³', '**3').replace('²', '**2').replace('³', '**3')

        # Handle exponentiation for any base and exponent (e.g., 2^3 or x^3)
        expression = re.sub(r'(\d+|\w+)\^(\d+)', r'(\1 ** \2)', expression)

        # Replace constants
        expression = expression.replace('π', str(math.pi)).replace('e', str(math.e))

        # Handle basic mathematical functions
        expression = re.sub(r'Cos\(([^)]+)\)', r'math.cos(\1)', expression)
        expression = re.sub(r'Sin\(([^)]+)\)', r'math.sin(\1)', expression)
        expression = re.sub(r'Tan\(([^)]+)\)', r'math.tan(\1)', expression)
        expression = re.sub(r'ln\(([^)]+)\)', r'math.log(\1)', expression)  # natural log
        expression = re.sub(r'log\(([^)]+)\)', r'math.log10(\1)', expression)  # base 10 log
        expression = re.sub(r'√\(([^)]+)\)', r'math.sqrt(\1)', expression)  # square root

        # Evaluate the expression
        result = eval(expression)
        return result
    except Exception as e:
        return str(e)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get('expression', '')

    # Evaluate the expression and return the result
    result = evaluate_expression(expression)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
