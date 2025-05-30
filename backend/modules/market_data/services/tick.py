import json
import asyncio
import datetime
from typing import Dict, Any

from backend.cache import TickCache, OrdersCache
from backend.common.consts import SQLServerConsts
from backend.modules.market_data.entities import Tick
from backend.modules.market_data.repositories import TickRepo
from backend.modules.market_data.dnse_service import DNSEService
from backend.modules.market_data.configs import Topics
from backend.modules.orders.entities import Orders, OrderStatus, OrderSide
from backend.modules.orders.repositories import OrdersRepo
from backend.modules.orders.services import OrdersService
from backend.modules.investors.entities import Accounts, Securities
from backend.modules.investors.repositories import AccountsRepo, SecuritiesRepo
from backend.utils.time_utils import TimeUtils
from backend.utils.logger import LOGGER


class TickService(DNSEService):
    topic = Topics.TICK
    repo = TickRepo

    @classmethod
    async def handle_msg(cls, client, userdata, msg):
        try:
            tick_payload = json.loads(msg.payload.decode())
            if not tick_payload["matchPrice"]:
                return

            """CHECK MATCHING ORDER ON COMING MESSAGE"""
            pending_orders = OrdersCache.get_pending_orders(symbol=tick_payload["symbol"])
            if pending_orders:
                for order_id, order in pending_orders.items():
                    print(f"Pending order: {order_id} - {order}")
                    if order["price"] == int(tick_payload["matchPrice"] * 1000):
                        OrdersCache.remove(
                            symbol=tick_payload["symbol"], order_id=order_id
                        )
                        await OrdersRepo.insert(
                            record={
                                Orders.id.name: order["id"],
                                Orders.account_id.name: order["account_id"],
                                Orders.side.name: order["side"],
                                Orders.symbol.name: order["symbol"],
                                Orders.price.name: order["price"],
                                Orders.qtty.name: order["qtty"],
                                Orders.order_type.name: order["order_type"],
                                Orders.status.name: OrderStatus.COMPLETED.value,
                                Orders.error.name: "",
                                "__created_at__": order["created_at"],
                            },
                            returning=False,
                        )
                        LOGGER.info(
                            f"ORDER {order['side']} {order['qtty']} [{order['symbol']} | {order['price']}] completed!"
                        )
                    else:
                        print("Order doesnt match!")

            """ADD MATCH PRICE TO CACHE"""
            TickCache.add(tick=tick_payload)

        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
