# import os
# from flask import Blueprint, request, jsonify, current_app
# from werkzeug.utils import secure_filename
# from db import get_db_connection

# restaurant_bp = Blueprint('restaurant_bp', __name__)

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def get_restaurant_id_for_user(user_id):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT r.restaurant_id FROM restaurants r JOIN users u ON r.owner_id = u.user_id WHERE u.user_id = %s", (user_id,))
#         result = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return result
#     except:
#         return None

# def verify_dish_ownership(dish_id, user_id):
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT d.dish_id FROM dishes d
#             JOIN restaurants r ON d.restaurant_id = r.restaurant_id
#             WHERE d.dish_id = %s AND r.owner_id = %s
#         """, (dish_id, user_id))
#         result = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return result is not None
#     except:
#         return False

# @restaurant_bp.route('/restaurant/profile', methods=['GET', 'OPTIONS'])
# def get_profile():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         user_id = request.args.get('user_id')
#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Restaurant not found"}), 404

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = %s", (info['restaurant_id'],))
#         restaurant = cursor.fetchone()
#         cursor.close()
#         conn.close()

#         if restaurant and restaurant.get('created_at'):
#             restaurant['created_at'] = restaurant['created_at'].isoformat()

#         return jsonify({"success": True, "data": restaurant}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/update-profile', methods=['POST', 'OPTIONS'])
# def update_profile():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         user_id = request.form.get('user_id')
#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         name = request.form.get('name', '')
#         description = request.form.get('description', '')
#         is_open = request.form.get('is_open', 'true') == 'true'

#         image_path = None
#         if 'image' in request.files:
#             file = request.files['image']
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'restaurants')
#                 os.makedirs(upload_dir, exist_ok=True)
#                 filepath = os.path.join(upload_dir, filename)
#                 file.save(filepath)
#                 image_path = f'uploads/restaurants/{filename}'

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         if image_path:
#             cursor.execute(
#                 "UPDATE restaurants SET name=%s, description=%s, is_open=%s, image=%s WHERE restaurant_id=%s",
#                 (name, description, is_open, image_path, info['restaurant_id'])
#             )
#         else:
#             cursor.execute(
#                 "UPDATE restaurants SET name=%s, description=%s, is_open=%s WHERE restaurant_id=%s",
#                 (name, description, is_open, info['restaurant_id'])
#             )

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "Profile updated successfully"}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/dishes', methods=['GET', 'OPTIONS'])
# def get_restaurant_dishes():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         user_id = request.args.get('user_id')
#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM dishes WHERE restaurant_id = %s ORDER BY dish_id DESC", (info['restaurant_id'],))
#         dishes = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "data": dishes}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/add-dish', methods=['POST', 'OPTIONS'])
# def add_dish():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         user_id = request.form.get('user_id')
#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         name = request.form.get('name', '').strip()
#         description = request.form.get('description', '')
#         price = request.form.get('price')
#         calories = request.form.get('calories', 0)
#         available = request.form.get('available', 'true') == 'true'

#         if not name or not price:
#             return jsonify({"success": False, "message": "Name and price are required"}), 400

#         image_path = None
#         if 'image' in request.files:
#             file = request.files['image']
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'dishes')
#                 os.makedirs(upload_dir, exist_ok=True)
#                 filepath = os.path.join(upload_dir, filename)
#                 file.save(filepath)
#                 image_path = f'uploads/dishes/{filename}'

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO dishes (restaurant_id, name, description, price, calories, image, available) VALUES (%s,%s,%s,%s,%s,%s,%s)",
#             (info['restaurant_id'], name, description, price, calories, image_path, available)
#         )
#         dish_id = cursor.lastrowid
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "Dish added successfully", "dish_id": dish_id}), 201

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/edit-dish', methods=['POST', 'OPTIONS'])
# def edit_dish():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         data = request.json
#         user_id = data.get('user_id')
#         dish_id = data.get('dish_id')

#         if not verify_dish_ownership(dish_id, user_id):
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         name = data.get('name')
#         description = data.get('description')
#         price = data.get('price')
#         calories = data.get('calories')
#         available = data.get('available', True)

#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute(
#             "UPDATE dishes SET name=%s, description=%s, price=%s, calories=%s, available=%s WHERE dish_id=%s",
#             (name, description, price, calories, available, dish_id)
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "Dish updated successfully"}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/dish/<int:dish_id>', methods=['DELETE', 'OPTIONS'])
# def delete_dish(dish_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         data = request.json if request.json else {}
#         user_id = data.get('user_id') or request.args.get('user_id')

#         if not verify_dish_ownership(dish_id, user_id):
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

# @restaurant_bp.route('/restaurant/orders', methods=['GET', 'OPTIONS'])
# def get_orders():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         user_id = request.args.get('user_id')
#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT o.*, u.name as student_name
#             FROM orders o
#             JOIN users u ON o.student_id = u.user_id
#             WHERE o.restaurant_id = %s AND o.status NOT IN ('completed','rejected')
#             ORDER BY o.created_at DESC
#         """, (info['restaurant_id'],))
#         orders = cursor.fetchall()

#         for order in orders:
#             if order.get('created_at'):
#                 order['created_at'] = order['created_at'].isoformat()
#             cursor.execute(
#                 "SELECT oi.quantity, d.name, oi.price FROM order_items oi JOIN dishes d ON oi.dish_id = d.dish_id WHERE oi.order_id = %s",
#                 (order['order_id'],)
#             )
#             order['items'] = cursor.fetchall()

#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "data": orders}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/update-order-status', methods=['POST', 'OPTIONS'])
# def update_order_status():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         data = request.json
#         user_id = data.get('user_id')
#         order_id = data.get('order_id')
#         status = data.get('status')
#         estimated_time = data.get('estimated_time')

#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         valid_statuses = ['accepted', 'rejected', 'preparing', 'ready', 'completed']
#         if status not in valid_statuses:
#             return jsonify({"success": False, "message": "Invalid status"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT restaurant_id FROM orders WHERE order_id = %s", (order_id,))
#         order = cursor.fetchone()
#         if not order or order['restaurant_id'] != info['restaurant_id']:
#             cursor.close()
#             conn.close()
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         if estimated_time:
#             cursor.execute("UPDATE orders SET status=%s, estimated_time=%s WHERE order_id=%s", (status, estimated_time, order_id))
#         else:
#             cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s", (status, order_id))

#         cursor.execute("INSERT INTO order_status_log (order_id, status) VALUES (%s,%s)", (order_id, status))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": f"Order {status}"}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @restaurant_bp.route('/restaurant/stats', methods=['GET', 'OPTIONS'])
# def restaurant_stats():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         user_id = request.args.get('user_id')
#         info = get_restaurant_id_for_user(user_id)
#         if not info:
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT COUNT(*) as count FROM dishes WHERE restaurant_id = %s", (info['restaurant_id'],))
#         total_dishes = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM orders WHERE restaurant_id = %s AND DATE(created_at) = CURDATE()", (info['restaurant_id'],))
#         orders_today = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM orders WHERE restaurant_id = %s", (info['restaurant_id'],))
#         orders_all_time = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM orders WHERE restaurant_id = %s AND status = 'pending'", (info['restaurant_id'],))
#         pending_orders = cursor.fetchone()['count']

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "success": True,
#             "data": {
#                 "total_dishes": total_dishes,
#                 "orders_today": orders_today,
#                 "orders_all_time": orders_all_time,
#                 "pending_orders": pending_orders
#             }
#         }), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from db import get_db_connection

restaurant_bp = Blueprint('restaurant_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_restaurant_id_for_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT r.restaurant_id FROM restaurants r WHERE r.owner_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except:
        return None

def verify_dish_ownership(dish_id, user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.dish_id FROM dishes d
            JOIN restaurants r ON d.restaurant_id = r.restaurant_id
            WHERE d.dish_id = %s AND r.owner_id = %s
        """, (dish_id, user_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except:
        return False

@restaurant_bp.route('/restaurant/profile', methods=['GET', 'OPTIONS'])
def get_profile():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = request.args.get('user_id')
        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Restaurant not found"}), 404

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = %s", (info['restaurant_id'],))
        restaurant = cursor.fetchone()
        cursor.close()
        conn.close()

        if restaurant and restaurant.get('created_at'):
            restaurant['created_at'] = restaurant['created_at'].isoformat()

        return jsonify({"success": True, "data": restaurant}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@restaurant_bp.route('/restaurant/update-profile', methods=['POST', 'OPTIONS'])
def update_profile():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = request.form.get('user_id')
        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        name = request.form.get('name', '')
        description = request.form.get('description', '')
        is_open = request.form.get('is_open', 'true') == 'true'
        phone = request.form.get('phone', '')

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'restaurants')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                image_path = f'uploads/restaurants/{filename}'

        conn = get_db_connection()
        cursor = conn.cursor()

        if image_path:
            cursor.execute(
                "UPDATE restaurants SET name=%s, description=%s, is_open=%s, image=%s, phone=%s WHERE restaurant_id=%s",
                (name, description, is_open, image_path, phone, info['restaurant_id'])
            )
        else:
            cursor.execute(
                "UPDATE restaurants SET name=%s, description=%s, is_open=%s, phone=%s WHERE restaurant_id=%s",
                (name, description, is_open, phone, info['restaurant_id'])
            )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@restaurant_bp.route('/restaurant/dishes', methods=['GET', 'OPTIONS'])
def get_restaurant_dishes():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = request.args.get('user_id')
        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM dishes WHERE restaurant_id = %s ORDER BY dish_id DESC",
            (info['restaurant_id'],)
        )
        dishes = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "data": dishes}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@restaurant_bp.route('/restaurant/add-dish', methods=['POST', 'OPTIONS'])
def add_dish():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = request.form.get('user_id')
        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        name = request.form.get('name', '').strip()
        description = request.form.get('description', '')
        price = request.form.get('price')
        calories = request.form.get('calories', 0)
        available = request.form.get('available', 'true') == 'true'
        out_of_stock = request.form.get('out_of_stock', 'false') == 'true'

        if not name or not price:
            return jsonify({"success": False, "message": "Name and price are required"}), 400

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'dishes')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                image_path = f'uploads/dishes/{filename}'

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dishes (restaurant_id, name, description, price, calories, image, available, out_of_stock) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (info['restaurant_id'], name, description, price, calories, image_path, available, out_of_stock)
        )
        dish_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Dish added successfully", "dish_id": dish_id}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@restaurant_bp.route('/restaurant/edit-dish', methods=['POST', 'OPTIONS'])
def edit_dish():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        user_id = data.get('user_id')
        dish_id = data.get('dish_id')

        if not verify_dish_ownership(dish_id, user_id):
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE dishes SET name=%s, description=%s, price=%s, calories=%s, available=%s, out_of_stock=%s WHERE dish_id=%s",
            (data.get('name'), data.get('description'), data.get('price'),
             data.get('calories'), data.get('available', True),
             data.get('out_of_stock', False), dish_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Dish updated successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@restaurant_bp.route('/restaurant/dish/<int:dish_id>', methods=['DELETE', 'OPTIONS'])
def delete_dish(dish_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json if request.json else {}
        user_id = data.get('user_id') or request.args.get('user_id')

        if not verify_dish_ownership(dish_id, user_id):
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
# GET ORDERS (with student contact)
# -----------------------------
@restaurant_bp.route('/restaurant/orders', methods=['GET', 'OPTIONS'])
def get_orders():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = request.args.get('user_id')
        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.*, u.name as student_name, u.phone as student_phone, u.email as student_email
            FROM orders o
            JOIN users u ON o.student_id = u.user_id
            WHERE o.restaurant_id = %s AND o.status NOT IN ('completed','rejected')
            ORDER BY o.created_at DESC
        """, (info['restaurant_id'],))
        orders = cursor.fetchall()

        for order in orders:
            if order.get('created_at'):
                order['created_at'] = order['created_at'].isoformat()
            cursor.execute(
                "SELECT oi.quantity, d.name, oi.price FROM order_items oi JOIN dishes d ON oi.dish_id = d.dish_id WHERE oi.order_id = %s",
                (order['order_id'],)
            )
            order['items'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "data": orders}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@restaurant_bp.route('/restaurant/update-order-status', methods=['POST', 'OPTIONS'])
def update_order_status():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        user_id = data.get('user_id')
        order_id = data.get('order_id')
        status = data.get('status')
        estimated_time = data.get('estimated_time')

        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        valid_statuses = ['accepted', 'rejected', 'preparing', 'ready', 'completed']
        if status not in valid_statuses:
            return jsonify({"success": False, "message": "Invalid status"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT restaurant_id FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        if not order or order['restaurant_id'] != info['restaurant_id']:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        if estimated_time:
            cursor.execute(
                "UPDATE orders SET status=%s, estimated_time=%s WHERE order_id=%s",
                (status, estimated_time, order_id)
            )
        else:
            cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s", (status, order_id))

        cursor.execute(
            "INSERT INTO order_status_log (order_id, status) VALUES (%s,%s)",
            (order_id, status)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": f"Order {status}"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# RESTAURANT STATS (with revenue)
# -----------------------------
@restaurant_bp.route('/restaurant/stats', methods=['GET', 'OPTIONS'])
def restaurant_stats():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        user_id = request.args.get('user_id')
        info = get_restaurant_id_for_user(user_id)
        if not info:
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        rid = info['restaurant_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as count FROM dishes WHERE restaurant_id = %s", (rid,))
        total_dishes = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE restaurant_id = %s AND DATE(created_at) = CURDATE()", (rid,))
        orders_today = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE restaurant_id = %s", (rid,))
        orders_all_time = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE restaurant_id = %s AND status = 'pending'", (rid,))
        pending_orders = cursor.fetchone()['count']

        cursor.execute("SELECT COALESCE(SUM(total_price),0) as revenue FROM orders WHERE restaurant_id = %s AND status='completed'", (rid,))
        total_revenue = float(cursor.fetchone()['revenue'])

        cursor.execute("SELECT COALESCE(SUM(total_price),0) as revenue FROM orders WHERE restaurant_id = %s AND status='completed' AND DATE(created_at)=CURDATE()", (rid,))
        daily_revenue = float(cursor.fetchone()['revenue'])

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "total_dishes": total_dishes,
                "orders_today": orders_today,
                "orders_all_time": orders_all_time,
                "pending_orders": pending_orders,
                "total_revenue": total_revenue,
                "daily_revenue": daily_revenue
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500