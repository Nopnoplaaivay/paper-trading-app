import streamlit as st
from typing import Dict,  Any

from src.web.requests_utils import RequestUtils

class OrdersService:
    @classmethod
    def place_order(cls, order_payload: Dict) -> Dict[str, Any]:
        response = RequestUtils.call_api("POST", "/orders-service/orders", payload=order_payload)
        if response:
            return response.get("data")
        return {"error": "Failed to place order"}
