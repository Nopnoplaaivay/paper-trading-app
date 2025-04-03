import json
import asyncio
import datetime
from typing import Dict, Any

from src.cache import OrderCache
from src.common.consts import SQLServerConsts
from src.modules.market_data.entities import Tick
from src.modules.market_data.repositories import TickRepo
from src.modules.market_data.dnse_service import DNSEService
from src.modules.market_data.configs import Topics
from src.modules.orders.entities import Orders, OrderStatus, OrderSide
from src.modules.orders.services import OrdersService
from src.modules.accounts.entities import Portfolios
from src.modules.accounts.repositories import PortfoliosRepo, AccountsRepo
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER


class TickService(DNSEService):
    topic = Topics.TICK
    repo = TickRepo

    @classmethod
    async def process_order(cls, payload_order: Dict, pending_order: Dict) -> None:
        payload_order["match_price"] = int(payload_order["match_price"] * 1000)
        if (
            payload_order["match_price"] == pending_order["price"]
            and payload_order["match_quantity"] >= pending_order["order_quantity"]
        ):
            await OrdersService.repo.update(
                record={
                    Orders.id.name: pending_order["id"],
                    Orders.order_status.name: OrderStatus.COMPLETED.value,
                },
                identity_columns=[Orders.id.name],
                returning=False,
            )
            await OrderCache.remove_order(
                symbol=payload_order["symbol"],
                side=payload_order["side"],
                order_id=pending_order["id"],
            )
            LOGGER.info(f"Order {pending_order['id']} - [{payload_order['side']} {payload_order['symbol']}] completed.")

            """
            
            """

    @classmethod
    async def on_message(cls, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            payload_order = {
                "symbol": payload.get("symbol"),
                "side": payload.get("side"),
                "match_price": payload.get("matchPrice"),
                "match_quantity": payload.get("matchQtty"),
            }
            if (
                not payload_order["symbol"]
                or not payload_order["side"]
                or not payload_order["match_price"]
                or not payload_order["match_quantity"]
            ):
                return
            print(payload_order)
            if payload_order["side"] == "SIDE_BUY":
                pending_orders = await OrderCache.get_orders(
                    symbol=payload_order["symbol"], side="SIDE_SELL"
                )
                if pending_orders:
                    for order_id, order in pending_orders.items():
                        await cls.process_order(payload_order, order)
            elif payload_order["side"] == "SIDE_SELL":
                pending_orders = await OrderCache.get_orders(
                    symbol=payload_order["symbol"], side="SIDE_BUY"
                )
                if pending_orders:
                    for order_id, order in pending_orders.items():
                        await cls.process_order(payload_order, order)

            # LOGGER.info(f"Received message... {payload_order["side"]} {payload_order["symbol"]}")
            await cls.repo.insert(
                record={
                    Tick.symbol.name: payload.get("symbol"),
                    Tick.trading_time.name: datetime.datetime.fromisoformat(
                        payload.get("time").replace("Z", "+00:00")
                    ) if payload.get("time") else TimeUtils.get_current_vn_time(),
                    Tick.side.name: payload_order["side"],
                    Tick.match_price.name: payload.get("matchPrice"),
                    Tick.match_quantity.name: payload.get("matchQtty"),
                    Tick.session.name: payload.get("session"),
                },
                returning=False,
            )
        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
