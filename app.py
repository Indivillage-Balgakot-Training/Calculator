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
logs_collection = db['logs']

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if users_collection.find_one({"username": username}):
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

    user = users_collection.find_one({"username": username})

    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True}), 200
    
    return jsonify({'success': False}), 401

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

        result = eval(expression, {"__builtins__": None}, allowed_names)

        logs_collection.insert_one({"username": username, "expression": expression, "result": result, "error": None})

        return jsonify({"result": result}), 200

    except Exception as e:
        logs_collection.insert_one({"username": username, "expression": expression, "result": None, "error": str(e)})
        return jsonify({"error": str(e)}), 400

@app.route('/api/logs/<username>', methods=['GET'])
def get_user_logs(username):
    try:
        logs = list(logs_collection.find({"username": username}, {"_id": 0}).sort("_id", -1).limit(5))
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
