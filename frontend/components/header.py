import streamlit as st

from frontend.cookies import WebCookieController
from frontend.services.auth import AuthService
from frontend.components import show_deposit_dialog
from backend.utils.logger import LOGGER

def display_app_header(page_name: str = "trading"):
    col1, col_spacer, col_deposit, col2 = st.columns([5, 5, 1, 1])

    if WebCookieController.get("loggedIn"):
        if WebCookieController.get("role") == "client":
            with col1:
                st.subheader("Trading App")
                account = WebCookieController.get("account")
                st.markdown(
                    f"Welcome {account} to Trading App! "
                    "You can manage your portfolio and place orders here."
                )

        elif WebCookieController.get("role") == "admin":
            if page_name == "trading":
                with col1:
                    st.subheader("Trading App")
                    st.markdown(
                        "Welcome to the Trading App! "
                        "You can manage your portfolio and place orders here."
                    )
            elif page_name == "admin":
                with col1:
                    st.subheader("Trading App")
                    st.markdown(
                        "Welcome to the Trading App! "
                        "As an admin, you can manage users and monitor activities."
                    )

        with col_deposit:
            deposit_clicked = st.button("Nạp tiền", key="header_deposit_btn", help="Nạp tiền vào tài khoản")
            if deposit_clicked:
                LOGGER.info("Deposit button clicked in header, calling dialog function.")
                show_deposit_dialog()

        with col2:
            logout_clicked = st.button("Đăng xuất", key="header_logout_btn", help="Log out of the application")
            if logout_clicked:
                LOGGER.info("Logout button clicked in header.")
                AuthService.logout_user()
                st.switch_page("app.py")

    st.divider()