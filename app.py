from flask import Flask, request, jsonify
from flask_cors import CORS
import math
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
client = MongoClient('mongodb+srv://Balgakot_app_training:SBhQqTzY7Go7sEXJ@validationapp.63rbg.mongodb.net/Dev_training?retryWrites=true&w=majority')
db = client['Dev_training']  # Your database name
users_collection = db['users']  # Collection to store user accounts
logs_collection = db['logs']  # Collection to store login attempts

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Check if the username already exists
    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    # Hash the password and store the user
    hashed_password = generate_password_hash(password)
    user_data = {"username": username, "password": hashed_password}
    
    try:
        result = users_collection.insert_one(user_data)
        return jsonify({"success": "User registered successfully", "user_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": f"Error registering user: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({"username": username})

    if user and check_password_hash(user['password'], password):
        # Log successful login
        logs_collection.insert_one({"username": username, "status": "success"})
        return jsonify({'success': True}), 200
    
    # Log failed login attempt
    logs_collection.insert_one({"username": username, "status": "failed"})
    return jsonify({'success': False}), 401

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
                               .replace('²', '**2') \
                               .replace('^', '**')

        result = eval(expression, {"__builtins__": None}, allowed_names)

        # Store the expression and result in MongoDB
        logs_collection.insert_one({"expression": expression, "result": result, "error": None})

        return jsonify({"result": result}), 200

    except Exception as e:
        logs_collection.insert_one({"expression": expression, "result": None, "error": str(e)})
        return jsonify({"error": str(e)}), 400

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        logs = list(logs_collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
