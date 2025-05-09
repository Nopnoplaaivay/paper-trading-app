import time
import streamlit as st
from typing import Optional

from backend.common.consts import CommonConsts
from frontend.cookies import WebCookieController
from frontend.requests_utils import RequestUtils
from backend.utils.logger import LOGGER
from backend.utils.jwt_utils import JWTUtils

# FAKE user roles for demo without real API call for roles
FAKE_ROLES = {
    "demo_user": "client",
    "broker_user": "broker",
    "admin_user": "admin",
}

class AuthService:
    @classmethod
    def login(cls, account, password) -> bool:
        LOGGER.info(f"Attempting login for user: {account}")

        payload = {"account": account, "password": password}
        response = RequestUtils.call_api("POST", "/auth-service/login", payload)
        if response and response.get("data").get("accessToken"):
            access_token = response.get("data").get("accessToken")
            account_id = response.get("data").get("accountId")

            print(f"Access Token: {access_token}")

            # Clear cookies before setting new ones
            WebCookieController.clear()

            # Set cookie with JWT token
            WebCookieController.set("accessToken", access_token, max_age=3600)
            WebCookieController.set("accountId", account_id, max_age=3600)
            WebCookieController.set("loggedIn", True, max_age=3600)

            decoded_payload = JWTUtils.decode_token(
                token=access_token, secret_key=CommonConsts.AT_SECRET_KEY
            )

            WebCookieController.set("account", account, max_age=3600)
            WebCookieController.set("userId", decoded_payload.get("userId"), max_age=3600)
            WebCookieController.set("role", decoded_payload.get("role"), max_age=3600)
            WebCookieController.set("sessionId", decoded_payload.get("sessionId"), max_age=3600)


            LOGGER.info(
                f"User {account} logged in with role {WebCookieController.get('role')}"
            )
            return True
        else:
            WebCookieController.set("loggedIn", False, max_age=3600)
            WebCookieController.set("loginError", "Invalid username or password.", max_age=3600)
            LOGGER.warning(f"Login failed for user: {account}")
            return False

    @classmethod
    def register(
        cls, account, password, confirm_password, role
    ) -> bool:
        LOGGER.info(f"Attempting registration for user: {account}")
        payload = {
            "account": account,
            "password": password,
            "confirm_password": confirm_password,
            "role": role
        }
        response = RequestUtils.call_api("POST", "/auth-service/register", payload)
        if response and response.get("status_code") == 200:
            LOGGER.info(f"User {account} registered successfully.")
            return True
        else:
            WebCookieController.set("loginError", "Registration failed.", max_age=3600)
            LOGGER.warning(f"Registration failed for user: {account}")
            return False

    @classmethod
    def logout_user(cls):
        LOGGER.info(f"Logging out user: {WebCookieController.get('account')}")
        payload = {
            "sessionId": WebCookieController.get("sessionId"),
            "userId": WebCookieController.get("userId"),
            "role": WebCookieController.get("role"),
        }
        response = RequestUtils.call_api("POST", "/auth-service/logout", payload)
        if response and response.get("status_code") == 200:
            LOGGER.info(f"User {WebCookieController.get('account')} logged out successfully.")
            WebCookieController.clear()
            st.success("Logged out successfully.")
            time.sleep(1)

    @classmethod
    def require_login(cls, role: Optional[str] = None):
        if not WebCookieController.get("loggedIn"):
            st.warning("Please log in to access this page.", icon="🔒")
            st.stop()

        if role:
            user_role = WebCookieController.get("role")
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
