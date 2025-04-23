import time
import streamlit as st

from src.web.auth import WebAPIs, AuthService
# from src.auth import login_user, register_user, initialize_auth_state, logout_user
from src.utils import logger

st.set_page_config(layout="centered", page_title="Login/Register")

# initialize_auth_state() # Make sure auth state is set up

# --- Main App Logic ---
# if st.session_state.logged_in:
#     # If already logged in, show welcome and logout
#     st.success(f"Welcome, {st.session_state.username}! (Role: {st.session_state.user_role})")
#     st.write("Navigate using the sidebar.")
#
#
# else:
    # If not logged in, show Login/Register options
st.title("Trading App Login")

login_tab, register_tab = st.tabs(["Login", "Register"])

with login_tab:
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        submitted = st.form_submit_button("Login")

        if submitted:
            if AuthService.login(login_username, login_password):
                st.rerun() # Rerun to update state and show welcome/sidebar
            else:
                st.error(st.session_state.get("login_error", "Login Failed"), icon="🚨")


with register_tab:
     with st.form("register_form"):
        reg_username = st.text_input("Choose Username", key="reg_user")
        reg_password = st.text_input("Choose Password", type="password", key="reg_pass")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        reg_role = st.selectbox("Select Role", ["client", "broker"])

        role_specific_box = st.empty()
        type_user = st.selectbox("Select User Type", ["Silver", "Gold", "VIP"], key="user_type")
        if reg_role == "broker":
            type_broker = type_user
            type_client = ""
        elif reg_role == "client":
            type_client = type_user
            type_broker = ""

        print(type_client)

        reg_submitted = st.form_submit_button("Register")

        if reg_submitted:
            if reg_password != reg_confirm_password:
                st.error("Passwords do not match.", icon="⚠️")
            elif not reg_username or not reg_password or not reg_role: # Basic validation
                st.error("Please fill in all fields.", icon="⚠️")
            else:
                # Call the registration API
                if reg_role == "broker" and not type_broker:
                    st.error("Please select broker type", icon="⚠️")
                elif reg_role == "client" and not type_client:
                    st.error("Please select client type", icon="⚠️")
                else:
                    # Call the registration API with broker/client types
                    if WebAPIs.register(reg_username, reg_password, reg_confirm_password, reg_role, type_broker, type_client):
                        st.success("Registration successful! Please log in.")
                        time.sleep(1)
                    else:
                        st.error(st.session_state.get("login_error", "Registration Failed"), icon="🚨")

# Add footer or other info if needed
st.caption("Trading App Demo v0.1")