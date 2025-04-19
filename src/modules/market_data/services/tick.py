import json
import asyncio
import datetime
from typing import Dict, Any

from src.cache import TickCache, OrdersCache
from src.common.consts import SQLServerConsts
from src.modules.market_data.entities import Tick
from src.modules.market_data.repositories import TickRepo
from src.modules.market_data.dnse_service import DNSEService
from src.modules.market_data.configs import Topics
from src.modules.orders.entities import Orders, OrderStatus, OrderSide
from src.modules.orders.repositories import OrdersRepo
from src.modules.orders.services import OrdersService
from src.modules.accounts.entities import Accounts, Securities
from src.modules.accounts.repositories import AccountsRepo, SecuritiesRepo
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER


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
