import hashlib
from .db import get_connection, create_user_table

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return False  # Username exists
    hashed = hash_password(password)
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()
    return True

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    data = c.fetchone()
    conn.close()
    return bool(data)
