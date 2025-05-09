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
            # Add PUT, DELETE etc. if needed
            else:
                LOGGER.error(f"Unsupported HTTP method: {method}")
                st.error(f"Internal Error: Unsupported HTTP method {method}")
                return None

            LOGGER.debug(f"API Response Status: {response.status_code}")
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            # Handle potential empty response for success codes like 204
            if response.status_code == 204 or not response.content:
                 return {"success": True, "status_code": response.status_code}
            return response.json()

        except requests.exceptions.ConnectionError:
            LOGGER.error(f"API Connection Error: Cannot connect to {url}")
            st.error("Connection Error: Could not reach API server.", icon="🚨")
            return None
        except requests.exceptions.Timeout:
            LOGGER.warning(f"API Timeout: {method} {url}")
            st.error("API Timeout.", icon="⏱️")
            return None
        except requests.exceptions.HTTPError as e:
            LOGGER.error(f"API HTTP Error: {e.response.status_code} for {url}. Response: {e.response.text}")
            error_detail = str(e)
            try:
                error_json = e.response.json()
                error_detail = error_json.get("detail", error_detail)
            except json.JSONDecodeError:
                error_detail = e.response.text[:200] # Show raw text if not JSON
            st.error(f"API Error {e.response.status_code}: {error_detail}", icon="🔥")
            return None # Indicate failure
        except Exception as e:
            LOGGER.error(f"Unexpected API call error ({method} {url}): {e}", exc_info=True)
            st.error(f"An unexpected error occurred while calling the API.", icon="❓")
            return None
