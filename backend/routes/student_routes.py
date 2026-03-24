# from flask import Blueprint, request, jsonify
# from db import get_db_connection

# student_bp = Blueprint('student_bp', __name__)

# @student_bp.route('/restaurants', methods=['GET', 'OPTIONS'])
# def get_restaurants():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM restaurants WHERE is_open = TRUE ORDER BY created_at DESC")
#         restaurants = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         for r in restaurants:
#             if r.get('created_at'):
#                 r['created_at'] = r['created_at'].isoformat()

#         return jsonify({"success": True, "data": restaurants}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @student_bp.route('/dishes/<int:restaurant_id>', methods=['GET', 'OPTIONS'])
# def get_dishes(restaurant_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM dishes WHERE restaurant_id = %s AND available = TRUE ORDER BY dish_id", (restaurant_id,))
#         dishes = cursor.fetchall()

#         cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
#         restaurant = cursor.fetchone()
#         cursor.close()
#         conn.close()

#         if not restaurant:
#             return jsonify({"success": False, "message": "Restaurant not found"}), 404

#         if restaurant.get('created_at'):
#             restaurant['created_at'] = restaurant['created_at'].isoformat()

#         return jsonify({"success": True, "data": {"restaurant": restaurant, "dishes": dishes}}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @student_bp.route('/order/create', methods=['POST', 'OPTIONS'])
# def create_order():
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         data = request.json
#         student_id = data.get('student_id')
#         restaurant_id = data.get('restaurant_id')
#         items = data.get('items')

#         if not all([student_id, restaurant_id, items]):
#             return jsonify({"success": False, "message": "Missing required fields"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT role FROM users WHERE user_id = %s", (student_id,))
#         user = cursor.fetchone()
#         if not user or user['role'] not in ('student', 'faculty'):
#             cursor.close()
#             conn.close()
#             return jsonify({"success": False, "message": "Unauthorized"}), 403

#         total_price = 0
#         item_prices = []

#         for item in items:
#             cursor.execute(
#                 "SELECT price FROM dishes WHERE dish_id = %s AND restaurant_id = %s AND available = TRUE",
#                 (item['dish_id'], restaurant_id)
#             )
#             dish = cursor.fetchone()
#             if not dish:
#                 cursor.close()
#                 conn.close()
#                 return jsonify({"success": False, "message": f"Invalid or unavailable dish"}), 400
#             item_total = float(dish['price']) * item['quantity']
#             total_price += item_total
#             item_prices.append(float(dish['price']))

#         cursor.execute(
#             "INSERT INTO orders (student_id, restaurant_id, total_price, status) VALUES (%s,%s,%s,'pending')",
#             (student_id, restaurant_id, total_price)
#         )
#         order_id = cursor.lastrowid

#         for i, item in enumerate(items):
#             cursor.execute(
#                 "INSERT INTO order_items (order_id, dish_id, quantity, price) VALUES (%s,%s,%s,%s)",
#                 (order_id, item['dish_id'], item['quantity'], item_prices[i])
#             )

#         cursor.execute("INSERT INTO order_status_log (order_id, status) VALUES (%s,'pending')", (order_id,))
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "message": "Order placed", "order_id": order_id}), 201

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @student_bp.route('/order/track/<int:order_id>', methods=['GET', 'OPTIONS'])
# def track_order(order_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         student_id = request.args.get('student_id')

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("""
#             SELECT o.*, r.name as restaurant_name
#             FROM orders o
#             JOIN restaurants r ON o.restaurant_id = r.restaurant_id
#             WHERE o.order_id = %s AND o.student_id = %s
#         """, (order_id, student_id))
#         order = cursor.fetchone()

#         if not order:
#             cursor.close()
#             conn.close()
#             return jsonify({"success": False, "message": "Order not found"}), 404

#         if order.get('created_at'):
#             order['created_at'] = order['created_at'].isoformat()

#         cursor.execute("""
#             SELECT oi.quantity, oi.price, d.name
#             FROM order_items oi
#             JOIN dishes d ON oi.dish_id = d.dish_id
#             WHERE oi.order_id = %s
#         """, (order_id,))
#         order['items'] = cursor.fetchall()

#         cursor.execute("SELECT status, timestamp FROM order_status_log WHERE order_id = %s ORDER BY timestamp", (order_id,))
#         logs = cursor.fetchall()
#         for log in logs:
#             if log.get('timestamp'):
#                 log['timestamp'] = log['timestamp'].isoformat()
#         order['status_log'] = logs

#         cursor.close()
#         conn.close()

#         return jsonify({"success": True, "data": order}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @student_bp.route('/orders/<int:student_id>', methods=['GET', 'OPTIONS'])
# def get_student_orders(student_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT o.*, r.name as restaurant_name
#             FROM orders o
#             JOIN restaurants r ON o.restaurant_id = r.restaurant_id
#             WHERE o.student_id = %s
#             ORDER BY o.created_at DESC
#         """, (student_id,))
#         orders = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         for o in orders:
#             if o.get('created_at'):
#                 o['created_at'] = o['created_at'].isoformat()

#         return jsonify({"success": True, "data": orders}), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

# @student_bp.route('/student/stats/<int:student_id>', methods=['GET', 'OPTIONS'])
# def student_stats(student_id):
#     if request.method == 'OPTIONS':
#         return jsonify({}), 200
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT COUNT(*) as count FROM orders WHERE student_id = %s", (student_id,))
#         total_orders = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM orders WHERE student_id = %s AND status = 'completed'", (student_id,))
#         completed = cursor.fetchone()['count']

#         cursor.execute("SELECT COUNT(*) as count FROM orders WHERE student_id = %s AND status NOT IN ('completed','rejected')", (student_id,))
#         active = cursor.fetchone()['count']

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "success": True,
#             "data": {
#                 "total_orders": total_orders,
#                 "completed_orders": completed,
#                 "active_orders": active
#             }
#         }), 200

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500

from flask import Blueprint, request, jsonify
from db import get_db_connection
import uuid

student_bp = Blueprint('student_bp', __name__)

# -----------------------------
# GET ALL OPEN RESTAURANTS
# -----------------------------
@student_bp.route('/restaurants', methods=['GET', 'OPTIONS'])
def get_restaurants():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*,
                COALESCE(AVG(rv.rating), 0) as avg_rating,
                COUNT(DISTINCT rv.review_id) as review_count
            FROM restaurants r
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

# -----------------------------
# GET DISHES FOR A RESTAURANT (with sorting + out_of_stock)
# -----------------------------
@student_bp.route('/dishes/<int:restaurant_id>', methods=['GET', 'OPTIONS'])
def get_dishes(restaurant_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        sort_by = request.args.get('sort', 'default')

        sort_map = {
            'price_asc': 'price ASC',
            'price_desc': 'price DESC',
            'calories_asc': 'calories ASC',
            'calories_desc': 'calories DESC',
            'popularity': 'order_count DESC',
            'default': 'dish_id ASC'
        }
        order_clause = sort_map.get(sort_by, 'dish_id ASC')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all dishes (available + out_of_stock, but NOT unavailable/hidden)
        cursor.execute(f"""
            SELECT * FROM dishes
            WHERE restaurant_id = %s AND available = TRUE
            ORDER BY {order_clause}
        """, (restaurant_id,))
        dishes = cursor.fetchall()

        cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = %s", (restaurant_id,))
        restaurant = cursor.fetchone()

        # Get average rating
        cursor.execute("""
            SELECT COALESCE(AVG(rating), 0) as avg_rating, COUNT(*) as review_count
            FROM reviews WHERE restaurant_id = %s
        """, (restaurant_id,))
        rating_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not restaurant:
            return jsonify({"success": False, "message": "Restaurant not found"}), 404

        if restaurant.get('created_at'):
            restaurant['created_at'] = restaurant['created_at'].isoformat()

        restaurant['avg_rating'] = round(float(rating_data['avg_rating']), 1)
        restaurant['review_count'] = rating_data['review_count']

        return jsonify({"success": True, "data": {"restaurant": restaurant, "dishes": dishes}}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# SEARCH — dishes + restaurants
# -----------------------------
@student_bp.route('/search', methods=['GET', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        q = request.args.get('q', '').strip()
        if not q:
            return jsonify({"success": True, "data": {"restaurants": [], "dishes": []}}), 200

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT restaurant_id, name, description, image, is_open
            FROM restaurants
            WHERE (name LIKE %s OR description LIKE %s) AND is_open = TRUE
            LIMIT 5
        """, (f'%{q}%', f'%{q}%'))
        restaurants = cursor.fetchall()

        cursor.execute("""
            SELECT d.dish_id, d.name, d.price, d.image, d.out_of_stock,
                   r.name as restaurant_name, r.restaurant_id
            FROM dishes d
            JOIN restaurants r ON d.restaurant_id = r.restaurant_id
            WHERE d.name LIKE %s AND d.available = TRUE AND r.is_open = TRUE
            LIMIT 10
        """, (f'%{q}%',))
        dishes = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "data": {"restaurants": restaurants, "dishes": dishes}}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# CREATE ORDER (multi-restaurant support)
# Each restaurant's items become a separate order, linked by cart_session
# -----------------------------
@student_bp.route('/order/create', methods=['POST', 'OPTIONS'])
def create_order():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        student_id = data.get('student_id')
        items_by_restaurant = data.get('items_by_restaurant')  # {restaurant_id: [{dish_id, quantity}]}

        if not student_id or not items_by_restaurant:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify student role
        cursor.execute("SELECT role, phone FROM users WHERE user_id = %s", (student_id,))
        user = cursor.fetchone()
        if not user or user['role'] not in ('student', 'faculty'):
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # Generate shared cart session ID for all orders in this batch
        cart_session = str(uuid.uuid4())[:8].upper()
        order_ids = []

        for restaurant_id, items in items_by_restaurant.items():
            restaurant_id = int(restaurant_id)
            total_price = 0
            item_prices = []

            for item in items:
                cursor.execute(
                    "SELECT price, out_of_stock FROM dishes WHERE dish_id = %s AND restaurant_id = %s AND available = TRUE",
                    (item['dish_id'], restaurant_id)
                )
                dish = cursor.fetchone()
                if not dish:
                    cursor.close()
                    conn.close()
                    return jsonify({"success": False, "message": f"Invalid dish {item['dish_id']}"}), 400
                if dish['out_of_stock']:
                    cursor.close()
                    conn.close()
                    return jsonify({"success": False, "message": f"Dish {item['dish_id']} is out of stock"}), 400

                item_total = float(dish['price']) * item['quantity']
                total_price += item_total
                item_prices.append(float(dish['price']))

            # Create order
            cursor.execute(
                "INSERT INTO orders (student_id, restaurant_id, total_price, status, cart_session) VALUES (%s,%s,%s,'pending',%s)",
                (student_id, restaurant_id, total_price, cart_session)
            )
            order_id = cursor.lastrowid

            for i, item in enumerate(items):
                cursor.execute(
                    "INSERT INTO order_items (order_id, dish_id, quantity, price) VALUES (%s,%s,%s,%s)",
                    (order_id, item['dish_id'], item['quantity'], item_prices[i])
                )
                # Update dish popularity
                cursor.execute(
                    "UPDATE dishes SET order_count = order_count + %s WHERE dish_id = %s",
                    (item['quantity'], item['dish_id'])
                )

            cursor.execute("INSERT INTO order_status_log (order_id, status) VALUES (%s,'pending')", (order_id,))
            order_ids.append(order_id)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Orders placed",
            "order_ids": order_ids,
            "cart_session": cart_session
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# TRACK SINGLE ORDER
# -----------------------------
@student_bp.route('/order/track/<int:order_id>', methods=['GET', 'OPTIONS'])
def track_order(order_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        student_id = request.args.get('student_id')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.*, r.name as restaurant_name, r.phone as restaurant_phone
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.order_id = %s AND o.student_id = %s
        """, (order_id, student_id))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Order not found"}), 404

        if order.get('created_at'):
            order['created_at'] = order['created_at'].isoformat()

        cursor.execute("""
            SELECT oi.quantity, oi.price, d.name, d.image
            FROM order_items oi
            JOIN dishes d ON oi.dish_id = d.dish_id
            WHERE oi.order_id = %s
        """, (order_id,))
        order['items'] = cursor.fetchall()

        cursor.execute("""
            SELECT status, timestamp FROM order_status_log
            WHERE order_id = %s ORDER BY timestamp
        """, (order_id,))
        logs = cursor.fetchall()
        for log in logs:
            if log.get('timestamp'):
                log['timestamp'] = log['timestamp'].isoformat()
        order['status_log'] = logs

        cursor.close()
        conn.close()

        return jsonify({"success": True, "data": order}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# GET ALL ORDERS FOR STUDENT
# -----------------------------
@student_bp.route('/orders/<int:student_id>', methods=['GET', 'OPTIONS'])
def get_student_orders(student_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.*, r.name as restaurant_name
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.student_id = %s
            ORDER BY o.created_at DESC
        """, (student_id,))
        orders = cursor.fetchall()
        cursor.close()
        conn.close()

        for o in orders:
            if o.get('created_at'):
                o['created_at'] = o['created_at'].isoformat()

        return jsonify({"success": True, "data": orders}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# STUDENT STATS (including total spending)
# -----------------------------
@student_bp.route('/student/stats/<int:student_id>', methods=['GET', 'OPTIONS'])
def student_stats(student_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE student_id = %s", (student_id,))
        total_orders = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE student_id = %s AND status = 'completed'", (student_id,))
        completed = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE student_id = %s AND status NOT IN ('completed','rejected')", (student_id,))
        active = cursor.fetchone()['count']

        cursor.execute("SELECT COALESCE(SUM(total_price), 0) as total FROM orders WHERE student_id = %s AND status = 'completed'", (student_id,))
        total_spent = float(cursor.fetchone()['total'])

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "total_orders": total_orders,
                "completed_orders": completed,
                "active_orders": active,
                "total_spent": total_spent
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# SUBMIT REVIEW
# -----------------------------
@student_bp.route('/review', methods=['POST', 'OPTIONS'])
def submit_review():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        user_id = data.get('user_id')
        restaurant_id = data.get('restaurant_id')
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not all([user_id, restaurant_id, rating]):
            return jsonify({"success": False, "message": "Missing fields"}), 400

        if not (1 <= int(rating) <= 5):
            return jsonify({"success": False, "message": "Rating must be between 1 and 5"}), 400

        # Verify user has ordered from this restaurant
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT order_id FROM orders
            WHERE student_id = %s AND restaurant_id = %s AND status = 'completed'
            LIMIT 1
        """, (user_id, restaurant_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "You can only review restaurants you have ordered from"}), 403

        cursor.execute("""
            INSERT INTO reviews (user_id, restaurant_id, rating, comment)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE rating = %s, comment = %s
        """, (user_id, restaurant_id, rating, comment, rating, comment))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Review submitted"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# GET REVIEWS FOR A RESTAURANT
# -----------------------------
@student_bp.route('/reviews/<int:restaurant_id>', methods=['GET', 'OPTIONS'])
def get_reviews(restaurant_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT rv.*, u.name as user_name
            FROM reviews rv
            JOIN users u ON rv.user_id = u.user_id
            WHERE rv.restaurant_id = %s
            ORDER BY rv.created_at DESC
        """, (restaurant_id,))
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()

        for r in reviews:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].isoformat()

        return jsonify({"success": True, "data": reviews}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# RAISE SUPPORT TICKET
# -----------------------------
@student_bp.route('/support/raise', methods=['POST', 'OPTIONS'])
def raise_ticket():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.json
        user_id = data.get('user_id')
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        if not all([user_id, subject, message]):
            return jsonify({"success": False, "message": "All fields required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO support_tickets (user_id, subject, message) VALUES (%s,%s,%s)",
            (user_id, subject, message)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Ticket raised successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -----------------------------
# GET MY TICKETS
# -----------------------------
@student_bp.route('/support/my-tickets/<int:user_id>', methods=['GET', 'OPTIONS'])
def my_tickets(user_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM support_tickets WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        tickets = cursor.fetchall()
        cursor.close()
        conn.close()

        for t in tickets:
            if t.get('created_at'):
                t['created_at'] = t['created_at'].isoformat()

        return jsonify({"success": True, "data": tickets}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500