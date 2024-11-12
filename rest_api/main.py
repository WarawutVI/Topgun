from flask import Flask, request, jsonify, Blueprint
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import psycopg2
import psycopg2.extras
import os

# ดึงค่า config จาก environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")  # ค่าเริ่มต้นคือ localhost
DB_PORT = os.getenv("DB_PORT", "5432")       # ค่าเริ่มต้นคือ 5432
API_TOKEN = os.getenv("API_TOKEN")

# สร้าง Flask app
app = Flask(__name__)

# ตั้งค่า CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# สร้าง authentication instance
auth = HTTPTokenAuth(scheme='Bearer')

# ฟังก์ชันตรวจสอบ token
@auth.verify_token
def verify_token(token):
    return token == API_TOKEN

# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูล
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# สร้าง API Blueprint สำหรับ version 1
api = Blueprint('api', __name__, url_prefix='/api')

# Routes ภายใต้ Blueprint api_v1
@api.route('/data', methods=['GET'])
@auth.login_required
def get_data():
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('SELECT * FROM data')
            users = cursor.fetchall()
            return jsonify([dict(user) for user in users])
    except (psycopg2.Error, Exception) as e:
        # Log the error for debugging
        print(f"Error fetching data: {e}")
        return jsonify({'error': 'Failed to retrieve data'}), 500
    finally:
        if conn:
            conn.close()

@api.route('/data', methods=['POST'])
@auth.login_required
def create_data():
    data = request.get_json()
    massage = data.get('massage')

    # Validate input data
    if not massage:
        return jsonify({'error': 'Invalid input data'}), 400

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                 'INSERT INTO data (massage) VALUES (%s) RETURNING *', (massage,)
            )
            new_data = cursor.fetchone()
            conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'error': 'This record already exists'}), 400
    except (psycopg2.Error, Exception) as e:
        conn.rollback()
        return jsonify({'error': f'Failed to create data: {e}'}), 500
    finally:
        conn.close()

    return jsonify(dict(new_data)), 201

# Register the Blueprint with the app
app.register_blueprint(api)

if __name__ == '__main__':
    app.run( debug=True)