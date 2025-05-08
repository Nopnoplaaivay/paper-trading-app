import time
import streamlit as st

st.set_page_config(layout="centered", page_title="Login/Register")

from src.web.auth import AuthService
from src.web.cookies import WebCookieController
from src.utils.logger import LOGGER


if WebCookieController.get("loggedIn"):
    st.success(f"Welcome, {WebCookieController.get('account')}!")
    time.sleep(1)
    try:
        st.switch_page("pages/trading_interface.py")
    except Exception as e:
        LOGGER.error(f"Switch page failed from login page: {e}")
        st.error("Redirect failed. Please use the sidebar.", icon="⚠️")

else:
    st.title("Login or Register")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form_page"):
            login_username = st.text_input("Username", key="login_user_page")
            login_password = st.text_input("Password", type="password", key="login_pass_page")
            submitted = st.form_submit_button("Login")

            if submitted:
                if AuthService.login(login_username, login_password):
                    st.success("Login Successful! Redirecting...")
                    time.sleep(1)
                    try:
                        role = WebCookieController.get("role")
                        if role == "admin":
                            target_page = "pages/trading_interface.py"
                            # target_page = "pages/admin_panel.py"
                        elif role == "broker":
                            target_page = "pages/trading_interface.py"
                            # target_page = "pages/broker_dashboard.py"
                        else:
                            target_page = "pages/trading_interface.py"
                        st.switch_page(target_page)
                    except Exception as e:
                        LOGGER.error(f"Switch page failed after login: {e}")
                        st.error("Login successful, but redirect failed. Please use sidebar.", icon="🚨")
                        st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.", icon="🚨")

    with register_tab:
         with st.form("register_form_page"):
            reg_username = st.text_input("Choose Username", key="reg_user_page")
            reg_password = st.text_input("Choose Password", type="password", key="reg_pass_page")
            reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_page")
            reg_role = st.selectbox("Select Role", ["client"], key="reg_role_page")

            reg_submitted = st.form_submit_button("Register")

            if reg_submitted:
                if reg_password != reg_confirm_password:
                    st.error("Passwords do not match.", icon="⚠️")
                elif not reg_username or not reg_password or not reg_role:
                    st.error("Please fill in all fields.", icon="⚠️")
                else:
                    if AuthService.register(reg_username, reg_password, reg_confirm_password, reg_role, "", ""):
                        st.success("Registration successful! Please proceed to Login.")
                        time.sleep(2)
                    else:
                        st.error(st.session_state.get("login_error", "Registration Failed."), icon="🚨")

    st.caption("Trading App Demo v0.1")