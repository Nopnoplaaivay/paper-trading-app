import time
import streamlit as st
from typing import Optional

from src.common.consts import CommonConsts
from src.web.auth import WebAPIs
from src.utils.logger import LOGGER
from src.utils.jwt_utils import JWTUtils

# FAKE user roles for demo without real API call for roles
FAKE_ROLES = {
    "demo_user": "client",
    "broker_user": "broker",
    "admin_user": "admin",
}


class AuthService:
    @classmethod
    def initialize_auth_state(cls):
        """Initializes session state variables related to authentication."""
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.user_role = None
            st.session_state.auth_token = None
            st.session_state.login_error = None

    @classmethod
    def login(cls, account, password) -> bool:
        LOGGER.info(f"Attempting login for user: {account}")
        st.session_state.login_error = None  # Clear previous errors

        response = WebAPIs.login(account=account, password=password)
        if response and response.get("data").get("accessToken"):
            access_token = response.get("data").get("accessToken")
            st.session_state.logged_in = True
            st.session_state.auth_token = access_token
            decoded_payload = JWTUtils.decode_token(
                token=access_token, secret_key=CommonConsts.AT_SECRET_KEY
            )

            st.session_state.username = account
            st.session_state.user_id = decoded_payload.get("userId")
            st.session_state.user_role = decoded_payload.get("role")
            print(f"Decoded payload: {decoded_payload}")
            LOGGER.info(
                f"User {st.session_state.username} logged in with role {st.session_state.user_role}"
            )
            return True
        else:
            st.session_state.logged_in = False
            st.session_state.login_error = (
                "Invalid username or password."  # Set error message
            )
            LOGGER.warning(f"Login failed for user: {account}")
            return False

    @classmethod
    def register(
        cls, account, password, confirm_password, role, type_broker, type_client
    ) -> bool:
        LOGGER.info(f"Attempting registration for user: {account}")
        st.session_state.login_error = None

        response = WebAPIs.register(
            account=account,
            password=password,
            confirm_password=confirm_password,
            role=role,
            type_broker=type_broker,
            type_client=type_client,
        )
        if response and response.get("status_code") == 200:
            LOGGER.info(f"User {account} registered successfully.")
            return True
        else:
            st.session_state.login_error = "Registration failed."  # Set error message
            LOGGER.warning(f"Registration failed for user: {account}")
            return False

# def logout_user():
#     """Logs the user out by clearing session state."""
#     LOGGER.info(f"Logging out user: {st.session_state.get('username')}")
#     keys_to_clear = ["logged_in", "username", "user_id", "user_role", "auth_token", "login_error"]
#     for key in keys_to_clear:
#         if key in st.session_state:
#             del st.session_state[key]
#     # Optionally call a backend /auth/logout endpoint if it exists
#     # call_api('POST', '/auth/logout')
#     st.success("Logged out successfully.")
#     time.sleep(1) # Pause briefly
#     st.rerun()
#
#
    @classmethod
    def require_login(cls, role: Optional[str] = None):
        """Decorator or function to protect pages/parts of pages."""
        cls.initialize_auth_state() # Ensure state exists
        if not st.session_state.logged_in:
            st.warning("Please log in to access this page.", icon="🔒")
            st.stop()

        if role:
            user_role = st.session_state.get("user_role")
            allowed = False
            if role == "broker" and user_role in ["broker", "admin"]:
                allowed = True
            elif role == "admin" and user_role == "admin":
                allowed = True
            elif role == "client" and user_role in ["client", "broker", "admin"]:
                allowed = True

            if not allowed:
                 st.error(f"Access Denied: You do not have the required '{role}' permissions.", icon="🚫")
                 st.stop()
