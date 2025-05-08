import time
import streamlit as st

from src.web.auth import AuthService
from src.utils.logger import LOGGER

st.set_page_config(layout="centered", page_title="Login/Register")

AuthService.initialize_auth_state()


if st.session_state.logged_in:
    st.success(f"Welcome, {st.session_state.username}! (Role: {st.session_state.user_role})")

st.title("Trading App Login")

login_tab, register_tab = st.tabs(["Login", "Register"])

with login_tab:
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        submitted = st.form_submit_button("Login")

        if submitted:
            if AuthService.login(login_username, login_password):
                if st.session_state.user_role == "admin":
                    try:
                        st.switch_page("pages/trading_interface.py")
                    except Exception as e:
                        LOGGER.error(f"Switch page failed: {e}")
                        st.error("Failed to switch page. Please try again.", icon="🚨")
            else:
                st.error(st.session_state.get("login_error", "Login Failed"), icon="🚨")

with register_tab:
     with st.form("register_form"):
        reg_username = st.text_input("Choose Username", key="reg_user")
        reg_password = st.text_input("Choose Password", type="password", key="reg_pass")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        reg_role = st.selectbox("Select Role", ["client", "broker"])

        type_broker = ""
        type_client = ""

        reg_submitted = st.form_submit_button("Register")

        if reg_submitted:
            if reg_password != reg_confirm_password:
                st.error("Passwords do not match.", icon="⚠️")
            elif not reg_username or not reg_password or not reg_role:
                st.error("Please fill in all fields.", icon="⚠️")
            else:
                if AuthService.register(reg_username, reg_password, reg_confirm_password, reg_role, type_broker, type_client):
                    st.success("Registration successful! Please log in.")
                    time.sleep(1)
                else:
                    st.error(st.session_state.get("login_error", "Registration Failed"), icon="🚨")

# Add footer or other info if needed
st.caption("Trading App Demo v0.1")