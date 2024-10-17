from flask import Flask, request, jsonify
from flask_cors import CORS
import math
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb+srv://Balgakot_app_training:SBhQqTzY7Go7sEXJ@validationapp.63rbg.mongodb.net/Dev_training?retryWrites=true&w=majority')
db = client['Dev_training']
users_collection = db['users']
calculation_collection = db['calculation']

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if len(username) < 3 or len(password) < 8:
        return jsonify({"error": "Username must be at least 3 characters and password must be at least 8 characters long."}), 400

    existing_user = users_collection.find_one({"username": {"$regex": f'^{username}$', "$options": "i"}})
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

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

    user = users_collection.find_one({"username": {"$regex": f'^{username}$', "$options": "i"}})

    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True, 'username': username}), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    expression = data.get('expression', '')
    username = data.get('username', '')

    if not expression or not username:
        return jsonify({"error": "No expression or username provided"}), 400

    try:
        allowed_names = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'pi': math.pi,
            'e': math.e,
        }

        expression = expression.replace('π', 'pi') \
                               .replace('√', 'sqrt') \
                               .replace('Sin', 'sin') \
                               .replace('Cos', 'cos') \
                               .replace('Tan', 'tan') \
                               .replace('ln', 'log') \
                               .replace('²', '**2') \
                               .replace('^', '**')

        # Evaluate the expression
        result = eval(expression, {"__builtins__": None}, allowed_names)

        # Store the calculation result in the 'calculation' collection
        calculation_collection.insert_one({
            "username": username,
            "expression": expression,
            "result": result,
            "error": None
        })

        return jsonify({"success": True, "result": result}), 200

    except Exception as e:
        # Log the error in the 'calculation' collection
        calculation_collection.insert_one({
            "username": username,
            "expression": expression,
            "result": None,
            "error": str(e)
        })
        print(f"Error evaluating expression '{expression}': {str(e)}")  # Log to console for debugging
        return jsonify({"error": "Calculation error. Please check your expression."}), 400

@app.route('/api/logs/<username>', methods=['GET'])
def get_user_logs(username):
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        logs = list(calculation_collection.find({"username": username}).sort("_id", -1).limit(5))
        
        # Create a more user-friendly response format
        response_logs = []
        for log in logs:
            response_logs.append({
                "username": log['username'],
                "expression": log['expression'],
                "result": log['result'],
                "error": log['error']
            })
        
        return jsonify(response_logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
