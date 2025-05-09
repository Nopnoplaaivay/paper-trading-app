import streamlit as st

from src.web.cookies import WebCookieController
from src.web.services.auth import AuthService
from src.web.components import show_deposit_dialog
from src.utils.logger import LOGGER

def display_app_header():
    col1, col_spacer, col_deposit, col2 = st.columns([5, 5, 1, 1])

    if WebCookieController.get("loggedIn"):
        with col1:
            st.subheader("Trading App")
            account = WebCookieController.get("account")
            st.markdown(
                f"Welcome {account} to Trading App! "
                "You can manage your portfolio and place orders here."
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
                st.switch_page("homepage.py")

    st.divider()