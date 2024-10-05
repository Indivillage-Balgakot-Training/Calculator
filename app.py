from flask import Flask, request, jsonify
from flask_cors import CORS
import math
from pymongo import MongoClient
<<<<<<< HEAD
=======
from werkzeug.security import generate_password_hash, check_password_hash

>>>>>>> bcaa675eb1a6a1824d828ad55ef36a77ff9c084f

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
client = MongoClient('mongodb+srv://Balgakot_app_training:SBhQqTzY7Go7sEXJ@validationapp.63rbg.mongodb.net/Dev_training?retryWrites=true&w=majority')
db = client['Dev_training']  # Your database name
collection = db['logs']  # Your collection name

# User database simulation
users = {
   'user': 'password'  # Replace with your desired username: password pair
}

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get('expression', '')

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
        
        result = eval(expression, {"_builtins_": None}, allowed_names)

        # Store the expression and result in MongoDB
<<<<<<< HEAD
=======
        logs_collection.insert_one({"expression": expression, "result": result, "error": None})
>>>>>>> bcaa675eb1a6a1824d828ad55ef36a77ff9c084f
        collection.insert_one({"expression": expression, "result": result, "error": None})

        return jsonify({"result": result}), 200

    except Exception as e:
        # Log the error to MongoDB
<<<<<<< HEAD
        collection.insert_one({"expression": expression, "result": None, "error": str(e)})
=======
        logs_collection.insert_one({"expression": expression, "result": None, "error": str(e)})
        collection.insert_one({"expression": expression, "result": None, "error": str(e)})

>>>>>>> bcaa675eb1a6a1824d828ad55ef36a77ff9c084f
        return jsonify({"error": str(e)}), 400

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        logs = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 401

if __name__ == '__main__':
    app.run(debug=True)
