from flask import Blueprint, jsonify, request
import mysql.connector

# Create a Blueprint for API routes
api = Blueprint('api', __name__)

# Database connection setup
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root_123",
        database="swa_v1"
    )

# 1. Create a new user (using URL parameters)
@api.route('/api/create_user', methods=['GET'])
def create_user():
    username = request.args.get('username')
    email = request.args.get('email')
    password = request.args.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, Email, and Password are required"}), 400


    conn = connect_db()
    cursor = conn.cursor()

    # Insert user into the database
    # Insert user into the database with hashed password
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                   (username, email, password))
    conn.commit()

    # Get the ID of the newly inserted user
    user_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({"message": "User created successfully", "user_id": user_id}), 201

# 2. Read all users (GET)
@api.route('/api/users', methods=['GET'])
def get_users():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    # Fetch all users from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(users)

# 3. Read a specific user by ID (GET)
@api.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    # Fetch user by ID from the database
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

# 4. Update an existing user (using URL parameters)
@api.route('/api/update_user', methods=['GET'])
def update_user():
    user_id = request.args.get('id')
    username = request.args.get('username')
    email = request.args.get('email')
    password = request.args.get('password')

    if not user_id or not username or not email or not password:
        return jsonify({"error": "ID, Username, Email, and Password are required"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    # Update user in the database
    cursor.execute("UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s", (username, email, password, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User updated successfully"})

# 5. Delete a user (using URL parameters)
@api.route('/api/delete_user', methods=['GET'])
def delete_user():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    # Delete user from the database
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted successfully"})
