import hashlib
import streamlit as st
from .db import get_connection, create_user_table

# Ensure table exists
create_user_table()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return False  # Username already exists
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

# ✅ UI function to show login/signup
def show_login_page():
    st.title("🔐 Login / Signup")

    option = st.radio("Choose an option", ["Login", "Signup"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Signup":
        if st.button("Create Account"):
            if signup_user(username, password):
                st.success("Account created! You can log in now.")
            else:
                st.error("Username already taken.")

    if option == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

def logout_user():
    # You can add logic here if needed, but it should be handled in the session state in app.py.
    return True
