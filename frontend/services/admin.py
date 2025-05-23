import streamlit as st
from typing import Dict, Any, List

from frontend.requests_utils import RequestUtils

class AdminService:
    @classmethod
    def get_all_users(cls) -> List[Dict[str, Any]]:
        response = RequestUtils.call_api("GET", "/admin-service/user_management")
        if response.get("statusCode") == 200:
            return response.get("data")
        return []

    @classmethod
    def update_user_role(cls, user_id: str, new_role: str) -> Dict[str, Any]:
        payload = {"user_id": user_id, "role": new_role}
        response = RequestUtils.call_api("POST", "/admin-service/user_management/update", payload=payload)
        return response

    @classmethod
    def get_all_orders(cls) -> List[Dict[str, Any]]:
        response = RequestUtils.call_api("POST", "/admin-service/orders_management")
        if response.get("statusCode") == 200:
            return response.get("data")
        return []

    @classmethod
    def cancel_order(cls, order_id: str) -> Dict[str, Any]:
        payload = {"order_id": order_id}
        response = RequestUtils.call_api("PUT", "/admin-service/orders_management/cancel", payload=payload)
        return response
