# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash
# from db import get_db_connection

# admin_bp = Blueprint('admin_bp', __name__)

# def verify_admin(admin_id):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT role FROM users WHERE user_id = %s", (admin_id,))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return user and user['role'] == 'admin'
#     except:
#         return False

# @admin_bp.route('/admin/create-restaurant-owner', methods=['POST', 'OPTIONS'])
# def create_restaurant_owner():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         data = request.json
#         admin_id = data.get('admin_id')
#         name = data.get('name', '').strip()
#         email = data.get('email', '').strip().lower()
#         password = data.get('password', '')
#         restaurant_name = data.get('restaurant_name', '').strip()
#         description = data.get('description', '')

#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         if not all([name, email, password, restaurant_name]):
#             return jsonify({"success": False, "message": "All fields are required"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
#         if cursor.fetchone():
#             cursor.close()
#             conn.close()
#             return jsonify({"success": False, "message": "Email already registered"}), 409

#         hashed = generate_password_hash(password)

#         try:
#             cursor.execute(
#                 "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'restaurant')",
#                 (name, email, hashed)
#             )
#             owner_id = cursor.lastrowid
#             cursor.execute(
#                 "INSERT INTO restaurants (owner_id, name, description, is_open) VALUES (%s, %s, %s, TRUE)",
#                 (owner_id, restaurant_name, description)
#             )
#             restaurant_id = cursor.lastrowid
#             conn.commit()
#         except Exception as e:
#             conn.rollback()
#             raise e
#         finally:
#             cursor.close()
#             conn.close()

#         return jsonify({
#             "success": True,
#             "message": "Restaurant owner created successfully",
#             "restaurant_id": restaurant_id
#         }), 201

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/stats', methods=['GET', 'OPTIONS'])
# def admin_stats():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         admin_id = request.args.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT COUNT(*) as count FROM users WHERE role IN ('student','faculty')")
#         total_users = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM restaurants")
#         total_restaurants = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM dishes")
#         total_dishes = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM orders")
#         total_orders = cursor.fetchone()['count']

#         cursor.execute("""
#             SELECT d.name as dish_name, r.name as restaurant_name, COUNT(oi.id) as order_count
#             FROM order_items oi
#             JOIN dishes d ON oi.dish_id = d.dish_id
#             JOIN restaurants r ON d.restaurant_id = r.restaurant_id
#             GROUP BY d.dish_id
#             ORDER BY order_count DESC
#             LIMIT 5
#         """)
#         top_dishes = cursor.fetchall()

#         cursor.execute("""
#             SELECT r.name, COUNT(o.order_id) as order_count
#             FROM orders o
#             JOIN restaurants r ON o.restaurant_id = r.restaurant_id
#             GROUP BY r.restaurant_id
#             ORDER BY order_count DESC
#             LIMIT 5
#         """)
#         top_restaurants = cursor.fetchall()

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "success": True,
#             "data": {
#                 "total_users": total_users,
#                 "total_restaurants": total_restaurants,
#                 "total_dishes": total_dishes,
#                 "total_orders": total_orders,
#                 "top_dishes": top_dishes,
#                 "top_restaurants": top_restaurants
#             }
#         }), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/users', methods=['GET', 'OPTIONS'])
# def get_all_users():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         admin_id = request.args.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT user_id, name, email, role, created_at FROM users ORDER BY created_at DESC")
#         users = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         for u in users:
#             if u.get('created_at'):
#                 u['created_at'] = u['created_at'].isoformat()

#         return jsonify({"success": True, "data": users}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
# def delete_user(user_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         admin_id = request.args.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "User deleted"}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/restaurants', methods=['GET', 'OPTIONS'])
# def get_all_restaurants():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         admin_id = request.args.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT r.*, u.name as owner_name, u.email as owner_email
#             FROM restaurants r
#             JOIN users u ON r.owner_id = u.user_id
#             ORDER BY r.created_at DESC
#         """)
#         restaurants = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         for r in restaurants:
#             if r.get('created_at'):
#                 r['created_at'] = r['created_at'].isoformat()

#         return jsonify({"success": True, "data": restaurants}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/toggle-restaurant', methods=['POST', 'OPTIONS'])
# def toggle_restaurant():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         data = request.json
#         admin_id = data.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         restaurant_id = data.get('restaurant_id')
#         is_open = data.get('is_open')

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("UPDATE restaurants SET is_open = %s WHERE restaurant_id = %s", (is_open, restaurant_id))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "Restaurant status updated"}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/dishes', methods=['GET', 'OPTIONS'])
# def get_all_dishes():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         admin_id = request.args.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT d.*, r.name as restaurant_name
#             FROM dishes d
#             JOIN restaurants r ON d.restaurant_id = r.restaurant_id
#             ORDER BY d.dish_id DESC
#         """)
#         dishes = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "data": dishes}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @admin_bp.route('/admin/dish/<int:dish_id>', methods=['DELETE', 'OPTIONS'])
# def delete_dish(dish_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         admin_id = request.args.get('admin_id')
#         if not verify_admin(admin_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM dishes WHERE dish_id = %s", (dish_id,))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "Dish deleted"}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_db_connection

admin_bp = Blueprint('admin_bp', __name__)

def verify_admin(admin_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role FROM users WHERE user_id = %s", (admin_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user and user['role'] == 'admin'
    except:
        return False

@admin_bp.route('/admin/create-restaurant-owner', methods=['POST', 'OPTIONS'])
def create_restaurant_owner():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        admin_id = data.get('admin_id')
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        restaurant_name = data.get('restaurant_name', '').strip()
        description = data.get('description', '')
        phone = data.get('phone', '')

        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        if not all([name, email, password, restaurant_name]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Email already registered"}), 409

        hashed = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role, phone) VALUES (%s,%s,%s,'restaurant',%s)",
                (name, email, hashed, phone)
            )
            owner_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO restaurants (owner_id, name, description, is_open, phone) VALUES (%s,%s,%s,TRUE,%s)",
                (owner_id, restaurant_name, description, phone)
            )
            restaurant_id = cursor.lastrowid
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

        return jsonify({
            "success": True,
            "message": "Restaurant owner created successfully",
            "restaurant_id": restaurant_id
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/admin/stats', methods=['GET', 'OPTIONS'])
def admin_stats():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role IN ('student','faculty')")
        total_users = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM restaurants")
        total_restaurants = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM dishes")
        total_dishes = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders")
        total_orders = cursor.fetchone()['count']

        cursor.execute("SELECT COALESCE(SUM(total_price),0) as revenue FROM orders WHERE status='completed'")
        total_revenue = float(cursor.fetchone()['revenue'])

        cursor.execute("""
            SELECT d.name as dish_name, r.name as restaurant_name, d.order_count
            FROM dishes d
            JOIN restaurants r ON d.restaurant_id = r.restaurant_id
            ORDER BY d.order_count DESC LIMIT 5
        """)
        top_dishes = cursor.fetchall()

        cursor.execute("""
            SELECT r.name, COUNT(o.order_id) as order_count
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            GROUP BY r.restaurant_id
            ORDER BY order_count DESC LIMIT 5
        """)
        top_restaurants = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "total_users": total_users,
                "total_restaurants": total_restaurants,
                "total_dishes": total_dishes,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "top_dishes": top_dishes,
                "top_restaurants": top_restaurants
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# GET ALL USERS — with filter by role + search
# -----------------------------
@admin_bp.route('/admin/users', methods=['GET', 'OPTIONS'])
def get_all_users():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        role_filter = request.args.get('role', '')
        search_q = request.args.get('search', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT user_id, name, email, role, phone, created_at FROM users WHERE 1=1"
        params = []

        if role_filter:
            query += " AND role = %s"
            params.append(role_filter)

        if search_q:
            query += " AND (name LIKE %s OR email LIKE %s)"
            params.extend([f'%{search_q}%', f'%{search_q}%'])

        query += " ORDER BY role, created_at DESC"

        cursor.execute(query, params)
        users = cursor.fetchall()

        # Count by role
        cursor.execute("""
            SELECT role, COUNT(*) as count FROM users
            GROUP BY role ORDER BY role
        """)
        role_counts = cursor.fetchall()

        cursor.close()
        conn.close()

        for u in users:
            if u.get('created_at'):
                u['created_at'] = u['created_at'].isoformat()

        return jsonify({"success": True, "data": users, "role_counts": role_counts}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/admin/user/<int:user_id>', methods=['DELETE', 'OPTIONS'])
def delete_user(user_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User deleted"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/admin/restaurants', methods=['GET', 'OPTIONS'])
def get_all_restaurants():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, u.name as owner_name, u.email as owner_email,
                COALESCE(AVG(rv.rating), 0) as avg_rating,
                COUNT(DISTINCT rv.review_id) as review_count
            FROM restaurants r
            JOIN users u ON r.owner_id = u.user_id
            LEFT JOIN reviews rv ON r.restaurant_id = rv.restaurant_id
            GROUP BY r.restaurant_id
            ORDER BY r.created_at DESC
        """)
        restaurants = cursor.fetchall()
        cursor.close()
        conn.close()

        for r in restaurants:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].isoformat()
            r['avg_rating'] = round(float(r['avg_rating']), 1)

        return jsonify({"success": True, "data": restaurants}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/admin/toggle-restaurant', methods=['POST', 'OPTIONS'])
def toggle_restaurant():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        admin_id = data.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE restaurants SET is_open = %s WHERE restaurant_id = %s",
            (data.get('is_open'), data.get('restaurant_id'))
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Restaurant status updated"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# GET ALL DISHES — grouped by restaurant
# -----------------------------
@admin_bp.route('/admin/dishes', methods=['GET', 'OPTIONS'])
def get_all_dishes():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        restaurant_filter = request.args.get('restaurant_id', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT d.*, r.name as restaurant_name, r.restaurant_id
            FROM dishes d
            JOIN restaurants r ON d.restaurant_id = r.restaurant_id
            WHERE 1=1
        """
        params = []

        if restaurant_filter:
            query += " AND d.restaurant_id = %s"
            params.append(restaurant_filter)

        query += " ORDER BY r.name, d.name"

        cursor.execute(query, params)
        dishes = cursor.fetchall()

        # Also get list of restaurants for filter dropdown
        cursor.execute("SELECT restaurant_id, name FROM restaurants ORDER BY name")
        restaurant_list = cursor.fetchall()

        cursor.close()
        conn.close()

        # Group dishes by restaurant
        grouped = {}
        for d in dishes:
            rname = d['restaurant_name']
            if rname not in grouped:
                grouped[rname] = {'restaurant_id': d['restaurant_id'], 'dishes': []}
            grouped[rname]['dishes'].append(d)

        return jsonify({
            "success": True,
            "data": dishes,
            "grouped": grouped,
            "restaurant_list": restaurant_list
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/admin/dish/<int:dish_id>', methods=['DELETE', 'OPTIONS'])
def delete_dish(dish_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dishes WHERE dish_id = %s", (dish_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Dish deleted"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# SUPPORT TICKETS — admin view
# -----------------------------
@admin_bp.route('/admin/support-tickets', methods=['GET', 'OPTIONS'])
def get_tickets():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        admin_id = request.args.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        status_filter = request.args.get('status', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT st.*, u.name as user_name, u.email as user_email
            FROM support_tickets st
            JOIN users u ON st.user_id = u.user_id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND st.status = %s"
            params.append(status_filter)

        query += " ORDER BY st.created_at DESC"
        cursor.execute(query, params)
        tickets = cursor.fetchall()
        cursor.close()
        conn.close()

        for t in tickets:
            if t.get('created_at'):
                t['created_at'] = t['created_at'].isoformat()

        return jsonify({"success": True, "data": tickets}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/admin/support-tickets/respond', methods=['POST', 'OPTIONS'])
def respond_ticket():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        admin_id = data.get('admin_id')
        if not verify_admin(admin_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        ticket_id = data.get('ticket_id')
        response = data.get('response', '').strip()
        status = data.get('status', 'responded')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE support_tickets SET admin_response=%s, status=%s WHERE ticket_id=%s",
            (response, status, ticket_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Response sent"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500