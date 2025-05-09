import streamlit as st
from typing import Dict, Any, List

from frontend.requests_utils import RequestUtils

class OrdersService:
    @classmethod
    def place_order(cls, order_payload: Dict) -> Dict[str, Any]:
        response = RequestUtils.call_api("POST", "/orders-service/orders", payload=order_payload)
        if response:
            return response.get("data")
        return {"error": "Failed to place order"}


    @classmethod
    def get_today_orders(cls) -> List[Dict[str, Any]]:
        st.session_state.login_error = None
        response = RequestUtils.call_api("GET", "/orders-service/orders")
        return response.get("data")