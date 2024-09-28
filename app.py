from flask import Flask, request, jsonify
from flask_cors import CORS
import math
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')  # Update with your MongoDB URI
db = client['Dev_training']  # Replace with your database name
collection = db['logs']  # Replace with your collection name

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression')

    if not expression:
        return jsonify({"error": "No expression provided"}), 400

    try:
        # Create a safe evaluation context
        allowed_names = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'pi': math.pi,
            'e': math.e,
        }

        # Replace custom symbols with their Python equivalents
        expression = expression.replace('π', 'pi') \
                               .replace('√', 'sqrt') \
                               .replace('Sin', 'sin') \
                               .replace('Cos', 'cos') \
                               .replace('Tan', 'tan') \
                               .replace('ln', 'log') \
                               .replace('²', '**2')  

        expression = expression.replace('^', '**')  
        
        result = eval(expression, {"__builtins__": None}, allowed_names)

        # Store the expression and result in MongoDB
        collection.insert_one({"expression": expression, "result": result})

        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
