from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth_bp', __name__)

def get_dashboard_for_role(role):
    if role in ('student', 'faculty'):
        return 'dash.html'
    elif role == 'restaurant':
        return 'restaurantdashboard.html'
    elif role == 'admin':
        return 'admin_dashboard.html'
    return 'login.html'

@auth_bp.route('/register', methods=['GET', 'POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not all([name, email, password]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        if email.endswith('@vitstudent.ac.in'):
            role = 'student'
        elif email.endswith('@vit.ac.in'):
            role = 'faculty'
        else:
            return jsonify({"success": False, "message": "Only VIT email addresses are allowed (@vitstudent.ac.in or @vit.ac.in)"}), 403

        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "This email is already registered"}), 409

        hashed = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed, role)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Account created successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@auth_bp.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.*, r.restaurant_id
            FROM users u
            LEFT JOIN restaurants r ON u.user_id = r.owner_id
            WHERE u.email = %s
        """, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not check_password_hash(user['password'], password):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user_id": user['user_id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "restaurant_id": user['restaurant_id'],
            "dashboard": get_dashboard_for_role(user['role'])
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500