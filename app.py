from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # cho phép request từ các client khác

DB_FILE = "users.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    return "API is running!"

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email hoặc password trống"}), 400
    hashed_password = generate_password_hash(password)
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()
        return jsonify({"message": "Đăng kí thành công!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email đã tồn tại"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email=?", (email,))
        row = cursor.fetchone()
    if row and check_password_hash(row[0], password):
        return jsonify({"message": "Đăng nhập thành công!"}), 200
    else:
        return jsonify({"error": "Email hoặc mật khẩu sai"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
