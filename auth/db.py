import sqlite3

DB_NAME = "auth_users.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_user_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()
