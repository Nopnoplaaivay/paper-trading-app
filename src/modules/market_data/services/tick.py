import json
import asyncio
import datetime

from src.cache import OrderCache
from src.common.consts import SQLServerConsts
from src.modules.market_data.entities import Tick
from src.modules.market_data.repositories import TickRepo
from src.modules.market_data.dnse_service import DNSEService
from src.modules.market_data.configs import Topics
from src.modules.orders.entities import Orders, OrderStatus, OrderSide
from src.modules.orders.services import OrdersService
from src.utils.time_utils import TimeUtils
from src.utils.logger import LOGGER


class TickService(DNSEService):
    topic = Topics.TICK
    repo = TickRepo

    @classmethod
    async def on_message(cls, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            LOGGER.info(f"Received message... {payload.get('side')} {payload.get('symbol')}")
            # await cls.repo.insert(
            #     record={
            #         Tick.symbol.name: payload.get("symbol"),
            #         Tick.trading_time.name: datetime.datetime.fromisoformat(
            #             payload.get("time").replace("Z", "+00:00")
            #         ) if payload.get("time") else TimeUtils.get_current_vn_time(),
            #         Tick.side.name: payload.get("side"),
            #         Tick.match_price.name: payload.get("matchPrice"),
            #         Tick.match_quantity.name: payload.get("matchQtty"),
            #         Tick.session.name: payload.get("session"),
            #     },
            #     returning=False,
            # )

            if payload.get("side") == "SIDE_BUY":
                pending_orders = await OrderCache.get_orders(
                    symbol=payload["symbol"], side=payload["side"]
                )
                if pending_orders:
                    for order_id, order in pending_orders.items():
                        print(f"Order ID: {order_id}, Order: {order}")
                        print(f"Type: {type(payload['matchPrice'])}, Order price: {type(order['price'])}")

                        msg_price = int(payload["matchPrice"] * 1000)
                        print(f"Message price: {msg_price}, Order price: {order['price']}")
                        print(f"Equals: {msg_price == order['price']}")
                        if int(payload["matchPrice"] * 1000) == order["price"]:
                            LOGGER.info(f"Updating order {order_id} - {payload['side']} {payload['symbol']} to completed.")
                            await OrdersService.repo.update(
                                record={
                                    Orders.id.name: order_id,
                                    Orders.order_status.name: OrderStatus.COMPLETED.value
                                },
                                identity_columns=[Orders.id.name],
                                returning=False
                            )
                            await OrderCache.remove_order(
                                symbol=payload["symbol"], side=payload["side"], order_id=order_id
                            )
                            LOGGER.info(f"Order {order_id} - {payload['side']} {payload['symbol']} completed.")
                            break
                        else:
                            print(f"Price from message: {int(payload['matchPrice'] * 1000)}, Order price: {order['price']}")
            elif payload.get("side") == "SIDE_SELL":
                pending_orders = await OrderCache.get_orders(
                    symbol=payload["symbol"], side=payload["side"]
                )
                if pending_orders:
                    for order_id, order in pending_orders.items():
                        if int(payload["matchPrice"] * 1000) == order["price"]:
                            await OrdersService.repo.update(
                                record={
                                    Orders.id.name: order_id,
                                    Orders.order_status.name: OrderStatus.COMPLETED.value
                                },
                                identity_columns=[Orders.id.name],
                                returning=False
                            )
                            await OrderCache.remove_order(
                                symbol=payload["symbol"], side=payload["side"], order_id=order_id
                            )
                            LOGGER.info(f"Order {order_id} - {payload['side']} {payload['symbol']} completed.")
                            break
                    
        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")
