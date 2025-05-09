import requests
import json
from typing import Optional, Dict, Any
import streamlit as st

from frontend.cookies import WebCookieController
from frontend.configs import WebConfigs
from backend.utils.logger import LOGGER

class RequestUtils:
    @classmethod
    def call_api(cls, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        token = WebCookieController.get("accessToken")
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{WebConfigs.BASE_API_URL}{endpoint}"
        LOGGER.debug(f"Calling API: {method} {url} Payload: {payload}")

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=5)
            elif method.upper() == 'POST':
                headers["Content-Type"] = "application/json" # Important for POST
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=5)
            elif method.upper() == 'PUT':
                headers["Content-Type"] = "application/json"
                response = requests.put(url, json=payload, headers=headers, timeout=10)
            else:
                LOGGER.error(f"Unsupported HTTP method: {method}")
                st.error(f"Internal Error: Unsupported HTTP method {method}")
                return None

            LOGGER.debug(f"API Response Status: {response.status_code}")

            # response.raise_for_status()
            # if response.status_code == 204 or not response.content:
            #      return {"success": True, "status_code": response.status_code}
            return response.json()

        except Exception as e:
            LOGGER.error(f"Unexpected API call error ({method} {url}): {e}", exc_info=True)
            st.error(f"An unexpected error occurred while calling the API.", icon="❓")
            return None
