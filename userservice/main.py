from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
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
CORS(app, resources={r"/api/v1/*": {"origins": "http://localhost:3000"}})



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
from flask import Blueprint
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')





# Routes ภายใต้ Blueprint api_v1
@api_v1.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    """ดึงข้อมูลผู้ใช้ทั้งหมด"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    users_list = [dict(user) for user in users]
    return jsonify(users_list)



@api_v1.route('/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    """ดึงข้อมูลผู้ใช้ตาม ID"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        abort(404, description="ไม่พบผู้ใช้")
    return jsonify(dict(user))






@api_v1.route('/users', methods=['POST'])
@auth.login_required
def create_user():
    """สร้างผู้ใช้ใหม่"""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING *',
            (name, email)
        )
        new_user = cursor.fetchone()
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': 'อีเมลนี้ถูกใช้งานแล้ว'}), 400
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        abort(500, description="เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์")
    cursor.close()
    conn.close()
    return jsonify(dict(new_user)), 201




@api_v1.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    """อัพเดทข้อมูลผู้ใช้"""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        abort(404, description="ไม่พบผู้ใช้")

    try:
        cursor.execute(
            'UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING *',
            (name, email, user_id)
        )
        updated_user = cursor.fetchone()
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': 'อีเมลนี้ถูกใช้งานแล้ว'}), 400
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        abort(500, description="ไม่สามารถอัพเดทข้อมูลได้")
    cursor.close()
    conn.close()
    return jsonify(dict(updated_user))




@api_v1.route('/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    """ลบผู้ใช้"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        abort(404, description="ไม่พบผู้ใช้")
    try:
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        abort(500, description="เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์")
    cursor.close()
    conn.close()
    return jsonify({"message": "ลบผู้ใช้สำเร็จ"})





# Health check route ที่ระดับ root (นอก blueprint)
@app.route('/health', methods=['GET'])
def health_check():
    """ตรวจสอบสถานะของ API และการเชื่อมต่อฐานข้อมูล"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception:
        abort(503, description="Database connection failed")





# ลงทะเบียน Blueprint
app.register_blueprint(api_v1)