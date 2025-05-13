from typing import Optional, Dict, Any

from frontend.cookies import WebCookieController
from frontend.services.orders import OrdersService
from backend.utils.logger import LOGGER

class OrderPayloadProcessor:
    @classmethod
    def create_payload(cls, form_data: dict) -> Optional[Dict[str, Any]]:
        if not form_data or not form_data.get("submitted"):
            LOGGER.warning("Payload creation skipped: No submitted form data.")
            return None

        try:
            symbol = form_data.get("symbol", "").strip().upper()
            side = form_data.get("submitted") # Should be 'SIDE_BUY' or 'SIDE_SELL'
            quantity = int(form_data.get("quantity", 0))
            order_type = form_data.get("order_type") # Should be 'LO' or 'MP'
            price = form_data.get("price") if order_type == "LO" else 0
            account_id = WebCookieController.get("accountId")
            print(f"Account ID: {account_id}")

            if not symbol or side not in ["SIDE_BUY", "SIDE_SELL"] or quantity <= 0 or order_type not in ["LO", "MP"]:
                LOGGER.error(f"Payload creation failed: Invalid base data. Symbol: {symbol}, Side: {side}, Qty: {quantity}, Type: {order_type}")
                return None
            if order_type == "LO" and (price is None or price <= 0):
                LOGGER.error(f"Payload creation failed: Invalid limit price for LO order. Price: {price}")
                return None

            order_payload = {
                "symbol": symbol,
                "side": side,
                "qtty": quantity,
                "order_type": order_type,
                "price": int(price * 1000),
                "account_id": account_id,
            }

            OrdersService.place_order(order_payload=order_payload)
            LOGGER.info(f"Successfully created order payload: {order_payload}")
            return order_payload

        except (KeyError, ValueError, TypeError) as e:
            LOGGER.error(f"Error creating payload from form data {form_data}: {e}", exc_info=True)
            return None
        except Exception as e:
             LOGGER.error(f"Unexpected error during payload creation: {e}", exc_info=True)
             return None