import requests
import json
from typing import Optional, Dict, Any
import streamlit as st

from src.web.configs import WebConfigs
from src.web.requests_utils import RequestUtils
from src.utils.logger import LOGGER


class WebAPIs:
    @classmethod
    def login(cls, account: str, password: str) -> Optional[Dict[str, Any]]:
        """Login API call."""
        payload = {"account": account, "password": password}
        return RequestUtils.call_api("POST", "/auth-service/login", payload)

    @classmethod
    def register(
        cls,
        account: str,
        password: str,
        confirm_password: str,
        role: str,
        type_broker: str,
        type_client: str,
    ) -> Optional[Dict[str, Any]]:
        payload = {
            "account": account,
            "password": password,
            "confirm_password": confirm_password,
            "role": role,
            "type_broker": type_broker,
            "type_client": type_client,
        }
        return RequestUtils.call_api("POST", "/auth-service/register", payload)


# --- Specific API call functions ---
#
# def api_login(username, password) -> Optional[Dict[str, Any]]:
#     return call_api('POST', '/auth/login', {"username": username, "password": password})
#
# def api_register(username, password, email) -> Optional[Dict[str, Any]]:
#      return call_api('POST', '/auth/register', {"username": username, "password": password, "email": email})
#
# def api_get_balance(user_id) -> Optional[Dict[str, Any]]:
#     return call_api('GET', f"/account/{user_id}/balance") # Endpoint depends on your API design
#
# def api_get_holdings(user_id) -> Optional[List[Dict[str, Any]]]:
#     # API might return a list directly
#     response = call_api('GET', f"/account/{user_id}/holdings")
#     # Ensure it returns a list even if the API might return a dict container
#     if isinstance(response, list):
#          return response
#     elif isinstance(response, dict) and 'holdings' in response and isinstance(response['holdings'], list):
#          return response['holdings']
#     elif response is not None: # Log unexpected format
#         logger.warning(f"Unexpected format for holdings response: {type(response)}")
#     return None # Return None on error or unexpected format
#
#
# def api_get_recent_orders(user_id) -> Optional[List[Dict[str, Any]]]:
#      response = call_api('GET', f"/orders/{user_id}/recent") # Endpoint depends on API design
#      if isinstance(response, list):
#          return response
#      elif isinstance(response, dict) and 'orders' in response and isinstance(response['orders'], list):
#          return response['orders']
#      elif response is not None:
#         logger.warning(f"Unexpected format for orders response: {type(response)}")
#      return None
#
# def api_place_order(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
#      return call_api('POST', '/orders', payload=payload)
#
# # --- Broker/Admin Specific API Calls (Placeholders - Require Backend Implementation) ---
#
# def api_get_broker_summary() -> Optional[Dict[str, Any]]:
#      # This needs a dedicated broker endpoint on the backend
#      logger.info("Calling placeholder api_get_broker_summary")
#      # return call_api('GET', '/broker/summary')
#      # FAKE RESPONSE FOR DEMO:
#      return {"total_aum": 150000000, "client_count": 25, "top_holding": "FPT"}
#
# def api_get_admin_users() -> Optional[List[Dict[str, Any]]]:
#     # Needs admin endpoint
#     logger.info("Calling placeholder api_get_admin_users")
#     # return call_api('GET', '/admin/users')
#     # FAKE RESPONSE FOR DEMO:
#     return [
#         {"user_id": "user_demo_123", "username": "demo_user", "role": "client", "email": "demo@test.com"},
#         {"user_id": "broker_001", "username": "broker_user", "role": "broker", "email": "broker@test.com"},
#         {"user_id": "admin_001", "username": "admin_user", "role": "admin", "email": "admin@test.com"},
#     ]
#
# def api_get_admin_all_orders() -> Optional[List[Dict[str, Any]]]:
#      # Needs admin endpoint
#      logger.info("Calling placeholder api_get_admin_all_orders")
#      # return call_api('GET', '/admin/orders/all')
#      # FAKE RESPONSE FOR DEMO:
#      # Reuse recent orders from session state if available, otherwise fake some more
#      orders = st.session_state.get('orders_real', [])
#      if not orders:
#           orders = [
#                {'order_id': 'B-1111', 'account_id': 'acc_123', 'side': 'BUY', 'symbol': 'FPT', 'order_type': 'LO', 'quantity': 100, 'limit_price': 1150, 'status': 'PENDING', 'created_at': datetime.now().isoformat()},
#                {'order_id': 'S-2222', 'account_id': 'acc_456', 'side': 'SELL', 'symbol': 'MWG', 'order_type': 'MP', 'quantity': 50, 'limit_price': None, 'status': 'COMPLETE', 'created_at': (datetime.now() - timedelta(minutes=5)).isoformat()},
#           ]
#      return orders
