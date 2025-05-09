import streamlit as st
from typing import Dict, Any

from frontend.cookies import WebCookieController
from frontend.requests_utils import RequestUtils


class InvestorsService:
    @classmethod
    def get_balance(cls) -> Dict[str, int]:
        st.session_state.login_error = None  # Clear previous errors
        response = RequestUtils.call_api("GET", "/investors-service/balance")
        if response:
            return response.get("data")
        return {
            "nav": 0,
            "available_cash": 0,
            "stock_value": 0,
            "purchasing_power": 0,
            "securing_amount": 0
        }

    @classmethod
    def get_all_holdings(cls) -> Dict[str, Any]:
        st.session_state.login_error = None
        response = RequestUtils.call_api("GET", "/investors-service/holdings")
        if response:
            return response.get("data")
        return None

    @classmethod
    def deposit(cls, amount: int) -> Dict[str, Any]:
        st.session_state.login_error = None
        payload = {
            "account_id": WebCookieController.get("accountId"),
            "amount": amount,
            "payment_method": "banking",
        }
        response = RequestUtils.call_api("POST", "/investors-service/deposit", payload=payload)
        return response
