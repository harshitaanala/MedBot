import streamlit as st
from auth.db import create_user_table, add_user, login_user

def show_login_page():
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome, {user['name']}!")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password")

def show_register_page():
    st.subheader("📝 Register")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if add_user(name, email, password):
            st.success("Registration successful. Please login.")
        else:
            st.warning("Email already registered.")

def show_auth_page():
    create_user_table()
    if "show_register" not in st.session_state:
        st.session_state.show_register = False

    if st.session_state.show_register:
        show_register_page()
        if st.button("Go to Login"):
            st.session_state.show_register = False
            st.experimental_rerun()
    else:
        show_login_page()
        if st.button("Go to Register"):
            st.session_state.show_register = True
            st.experimental_rerun()
