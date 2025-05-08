import streamlit as st

from src.web.cookies import WebCookieController
from src.web.auth import AuthService
from src.utils.logger import LOGGER

def display_app_header():
    col1, col_spacer, col2 = st.columns([4, 4, 1])

    if WebCookieController.get("loggedIn"):
        with col1:
            st.subheader("Trading App")
            account = WebCookieController.get("account")
            st.markdown(
                f"Welcome {account} to Trading App! "
                "You can manage your portfolio and place orders here."
            )

        with col2:
            logout_clicked = st.button("Logout", key="header_logout_btn", help="Log out of the application")
            if logout_clicked:
                LOGGER.info("Logout button clicked in header.")
                AuthService.logout_user()
                st.switch_page("homepage.py")

    st.divider()