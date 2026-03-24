# import os
# from flask import Flask, send_from_directory, request as flask_request
# from flask_cors import CORS
# from config import UPLOAD_FOLDER, SECRET_KEY

# from routes.auth_routes import auth_bp
# from routes.admin_routes import admin_bp
# from routes.restaurant_routes import restaurant_bp
# from routes.student_routes import student_bp

# app = Flask(__name__)
# app.config['SECRET_KEY'] = SECRET_KEY
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# CORS(app, supports_credentials=True)
# app.config['CORS_HEADERS'] = 'Content-Type'

# # @app.before_request
# # def handle_options():
# #     if flask_request.method == 'OPTIONS':
# #         from flask import Response
# #         res = Response()
# #         res.headers['Access-Control-Allow-Origin'] = '*'
# #         res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
# #         res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
# #         return res, 200

# # @app.after_request
# # def after_request(response):
# #     response.headers.add('Access-Control-Allow-Origin', '*')
# #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
# #     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
# #     return response

# app.register_blueprint(auth_bp)
# app.register_blueprint(admin_bp)
# app.register_blueprint(restaurant_bp)
# app.register_blueprint(student_bp)

# @app.route('/uploads/<path:filename>')
# def uploaded_file(filename):
#     return send_from_directory(UPLOAD_FOLDER, filename)

# @app.route('/')
# def home():
#     return "V Meal backend running"

# if __name__ == '__main__':
#     os.makedirs(os.path.join(UPLOAD_FOLDER, 'restaurants'), exist_ok=True)
#     os.makedirs(os.path.join(UPLOAD_FOLDER, 'dishes'), exist_ok=True)
#     app.run(debug=True, port=5000)

import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import UPLOAD_FOLDER, SECRET_KEY

from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.restaurant_routes import restaurant_bp
from routes.student_routes import student_bp

app = Flask(__name__)

# -------------------------------
# CONFIG
# -------------------------------
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ✅ APPLY CORS HERE (IMPORTANT)
CORS(app, resources={r"/*": {"origins": "*"}})

# -------------------------------
# REGISTER ROUTES
# -------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(restaurant_bp)
app.register_blueprint(student_bp)

# -------------------------------
# SERVE UPLOADED IMAGES
# -------------------------------
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -------------------------------
# TEST ROUTE
# -------------------------------
@app.route('/')
def home():
    return "V Meal backend running"

# -------------------------------
# RUN SERVER (ONLY HERE)
# -------------------------------
if __name__ == '__main__':
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'restaurants'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'dishes'), exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)