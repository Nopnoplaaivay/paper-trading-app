import streamlit as st

st.set_page_config(layout="centered", page_title="Welcome - Trading App Simulation")

from src.web.cookies import WebCookieController
from src.web.services import AuthService


st.title("Welcome to the Trading App!")
st.markdown("---")

st.header("Simulate real-time stock trading.")
st.write("""
Explore market data, practice your strategies, and manage your virtual portfolio.
Get started by logging in or creating an account.
""")
st.markdown("---")

# --- Navigation based on Login Status ---
if WebCookieController.get("loggedIn"):
    username = WebCookieController.get("account")
    st.success(f"You are logged in as **{username}**.")
    st.write("Go to your trading dashboard:")


    if st.button("Go to Trading Interface", type="primary"):
        try:
            role = WebCookieController.get("role")
            if role == "admin":
                target_page = "pages/trading_interface.py"
                # target_page = "pages/admin_panel.py"
            elif role == "broker":
                target_page = "pages/trading_interface.py"
                # target_page = "pages/broker_dashboard.py"
            else:  # Default to client
                target_page = "pages/trading_interface.py"
            st.switch_page(target_page)
        except Exception as e:
             st.error("Could not switch page automatically. Please use the sidebar.", icon="⚠️")

    if st.button("Logout"):
         AuthService.logout_user()

else:
    st.info("Ready to start trading?")
    if st.button("Login or Register", type="primary"):
        try:
            st.switch_page("pages/login_register.py")
        except Exception as e:
            st.error("Could not navigate to login page. Please check the application structure.", icon="🚨")

st.caption("Trading App Demo v0.1")