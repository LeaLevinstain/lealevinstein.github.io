from flask import Flask, request, jsonify, session
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'hardcoded_secret_key_123'  # Bug 1: Hardcoded secret key

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Bug 2: SQL Injection vulnerability
@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SECURE: Use parameterized query to prevent SQL injection
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[3],
            'created_at': user[4]
        })
    return jsonify({'error': 'User not found'}), 404

# Bug 3: Inefficient database query in loop (N+1 problem)
@app.route('/users', methods=['GET'])
def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # EFFICIENT: Single query to fetch all users
    cursor.execute("SELECT id, username, email, created_at FROM users")
    users_data = cursor.fetchall()
    
    users = []
    for user in users_data:
        users.append({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'created_at': user[3]
        })
    
    conn.close()
    return jsonify(users)

# Bug 4: Logic error in password validation
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # FIXED: Hash input password before comparison
        stored_password = user[2]
        input_password_hash = hashlib.md5(password.encode()).hexdigest()
        if input_password_hash == stored_password:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return jsonify({'message': 'Login successful'})
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Bug 5: Missing input validation and rate limiting
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # Missing validation for username/password length, email format, etc.
    
    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Hash password before storing
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, datetime.now())
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 409

# Bug 6: Insecure session management
@app.route('/logout', methods=['POST'])
def logout():
    # INSECURE: Only clearing session, not invalidating server-side
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')  # Bug 7: Debug mode in production