from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    operand1 = data.get('operand1')
    operator = data.get('operator')
    operand2 = data.get('operand2')

    print(f"Received: {operand1}, {operator}, {operand2}")  # Debugging line

    try:
        # Ensure the operands are valid numbers
        operand1 = float(operand1)
        operand2 = float(operand2)

        if operator == 'ADD':
            result = operand1 + operand2
        elif operator == 'SUBTRACT':
            result = operand1 - operand2
        elif operator == 'MULTIPLY':
            result = operand1 * operand2
        elif operator == 'DIVIDE':
            if operand2 == 0:
                return jsonify({"error": "Cannot divide by zero"}), 400
            result = operand1 / operand2
        else:
            return jsonify({"error": "Invalid operator"}), 400

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
