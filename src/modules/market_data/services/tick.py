import json
import asyncio
import datetime
from typing import Dict, Any

from src.redis import TickCache, OrdersCache
from src.common.consts import SQLServerConsts
from src.modules.market_data.entities import Tick
from src.modules.market_data.repositories import TickRepo
from src.modules.market_data.dnse_service import DNSEService
from src.modules.market_data.configs import Topics
from src.modules.orders.entities import Orders, OrderStatus, OrderSide
from src.modules.orders.repositories import OrdersRepo
from src.modules.orders.services import OrdersService
from src.modules.accounts.entities import Accounts, Portfolios
from src.modules.accounts.repositories import AccountsRepo, PortfoliosRepo
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
            pending_orders = await OrdersCache.get_all(symbol=tick_payload["symbol"])
            if pending_orders:
                for order_id, order in pending_orders.items():
                    print(f"Pending order: {order_id} - {order}")
                    if order["price"] == int(tick_payload["matchPrice"] * 1000):
                        await OrdersCache.remove(
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
            await TickCache.add(tick=tick_payload)
            # if tick_payload["matchPrice"] == order["price"]:
            # complete_orders

            # await OrdersService.process_order(
            #     payload_order=tick_payload, pending_order=order
            # )
            # await OrdersCache.remove_order(
            #     symbol=tick_payload["symbol"], order_id=order_id
            # )

        except Exception as e:
            raise Exception(f"Failed to decode message: {e}")

            # if payload_order["side"] == "SIDE_BUY":
            #     pending_orders = await OrderCache.get_orders(
            #         symbol=payload_order["symbol"], side="SIDE_SELL"
            #     )
            #     if pending_orders:
            #         for order_id, order in pending_orders.items():
            #             await cls.process_order(payload_order, order)
            # elif payload_order["side"] == "SIDE_SELL":
            #     pending_orders = await OrderCache.get_orders(
            #         symbol=payload_order["symbol"], side="SIDE_BUY"
            #     )
            #     if pending_orders:
            #         for order_id, order in pending_orders.items():
            #             await cls.process_order(payload_order, order)

            # await cls.repo.insert(
            #     record={
            #         Tick.symbol.name: payload_order["symbol"],
            #         Tick.trading_time.name: (
            #             datetime.datetime.fromisoformat(
            #                 payload.get("time").replace("Z", "+00:00")
            #             )
            #             if payload.get("time")
            #             else TimeUtils.get_current_vn_time()
            #         ),
            #         Tick.side.name: payload_order["side"],
            #         Tick.match_price.name: payload_order["match_price"],
            #         Tick.match_quantity.name: payload_order["match_quantity"],
            #         Tick.session.name: payload.get("session"),
            #     },
            #     returning=False,
            # )

    @classmethod
    async def process_order(cls, payload_order: Dict, pending_order: Dict) -> None:
        payload_order["match_price"] = int(payload_order["match_price"] * 1000)
        if payload_order["match_price"] == pending_order["price"]:
            await OrdersService.repo.update(
                record={
                    Orders.id.name: pending_order["id"],
                    Orders.order_status.name: OrderStatus.COMPLETED.value,
                },
                identity_columns=[Orders.id.name],
                returning=False,
            )
            await OrderCache.remove_order(
                symbol=pending_order["symbol"],
                side=pending_order["side"],
                order_id=pending_order["id"],
            )
            LOGGER.info(
                f"[SUCCESS] {pending_order['side']} {pending_order['order_quantity']} [{pending_order['symbol']} | {pending_order['price']}] - {pending_order['id']}"
            )

            # Update account balance when completed
            accounts = await AccountsRepo.get_by_condition(
                {Accounts.id.name: pending_order["account_id"]}
            )
            account = accounts[0]
            order_cost = pending_order["price"] * pending_order["order_quantity"]

            """UPDATE ACCOUNT WHEN ORDER COMPLETED"""
            if pending_order["side"] == "SIDE_BUY":
                securities = await PortfoliosRepo.get_by_condition(
                    conditions={
                        Portfolios.account_id.name: pending_order["account_id"],
                        Portfolios.symbol.name: payload_order["symbol"],
                    }
                )
                if len(securities) == 0:
                    await PortfoliosRepo.insert(
                        record={
                            Portfolios.account_id.name: pending_order["account_id"],
                            Portfolios.symbol.name: payload_order["symbol"],
                            Portfolios.price.name: payload_order["match_price"],
                            Portfolios.quantity.name: pending_order["order_quantity"],
                            Portfolios.avg_price.name: payload_order["match_price"],
                            Portfolios.total_cost.name: order_cost,
                            Portfolios.total_value.name: order_cost,
                            Portfolios.realized_profit.name: 0,
                            Portfolios.created_at.name: TimeUtils.get_current_vn_time(),
                            Portfolios.updated_at.name: TimeUtils.get_current_vn_time(),
                        },
                        returning=False,
                    )
                else:
                    security = securities[0]
                    total_quantity = (
                        security[Portfolios.quantity.name]
                        + pending_order["order_quantity"]
                    )
                    total_cost = (
                        security[Portfolios.avg_price.name]
                        * security[Portfolios.quantity.name]
                        + order_cost
                    )
                    avg_price = total_cost / total_quantity
                    total_value = total_quantity * payload_order["match_price"]
                    realized_profit = total_value - total_cost

                    """UPDATE PORTFOLIOS WHEN BUY ORDER COMPLETED"""
                    await PortfoliosRepo.update(
                        record={
                            Portfolios.account_id.name: pending_order["account_id"],
                            Portfolios.symbol.name: payload_order["symbol"],
                            Portfolios.price.name: payload_order["match_price"],
                            Portfolios.quantity.name: total_quantity,
                            Portfolios.avg_price.name: avg_price,
                            Portfolios.total_cost.name: total_cost,
                            Portfolios.total_value.name: total_value,
                            Portfolios.realized_profit.name: realized_profit,
                            Portfolios.updated_at.name: TimeUtils.get_current_vn_time(),
                        },
                        identity_columns=[
                            Portfolios.account_id.name,
                            Portfolios.symbol.name,
                        ],
                        returning=False,
                    )
                """
                WHEN BUY ORDER COMPLETED, 
                ONLY DECREASE SECURING AMOUNT AND INCREASE STOCK VALUE
                """
                update_securing_amount = (
                    account[Accounts.securing_amount.name] - order_cost
                )
                update_stock_value = account[Accounts.stock_value.name] + order_cost
                await AccountsRepo.update(
                    record={
                        Accounts.id.name: pending_order["account_id"],
                        Accounts.securing_amount.name: update_securing_amount,
                        Accounts.stock_value.name: update_stock_value,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                )
            elif pending_order["side"] == "SIDE_SELL":
                securities = await PortfoliosRepo.get_by_condition(
                    conditions={
                        Portfolios.account_id.name: pending_order["account_id"],
                        Portfolios.symbol.name: payload_order["symbol"],
                    }
                )
                if len(securities) == 0:
                    raise Exception(
                        f"Account {pending_order['account_id']} has no {payload_order['symbol']} security."
                    )

                security = securities[0]
                total_quantity = (
                    security[Portfolios.quantity.name] - pending_order["order_quantity"]
                )
                if total_quantity == 0:
                    await PortfoliosRepo.delete(
                        conditions={
                            Portfolios.account_id.name: pending_order["account_id"],
                            Portfolios.symbol.name: payload_order["symbol"],
                        },
                        returning=False,
                    )
                else:
                    total_cost = (
                        security[Portfolios.avg_price.name]
                        * security[Portfolios.quantity.name]
                    )
                    total_value = total_quantity * payload_order["match_price"]
                    realized_profit = total_value - total_cost
                    await PortfoliosRepo.update(
                        record={
                            Portfolios.account_id.name: pending_order["account_id"],
                            Portfolios.symbol.name: payload_order["symbol"],
                            Portfolios.price.name: payload_order["match_price"],
                            Portfolios.quantity.name: total_quantity,
                            Portfolios.total_cost.name: total_cost,
                            Portfolios.total_value.name: total_value,
                            Portfolios.realized_profit.name: realized_profit,
                            Portfolios.updated_at.name: TimeUtils.get_current_vn_time(),
                        },
                        identity_columns=[
                            Portfolios.account_id.name,
                            Portfolios.symbol.name,
                        ],
                        returning=False,
                    )

                """
                WHEN SELL ORDER COMPLETED,
                INCREASE AVAILABLE CASH, WITHDRAWABLE CASH, 
                DECREASE STOCK VALUE, RECEIVING AMOUNT
                """
                update_available_cash = (
                    account[Accounts.available_cash.name] + order_cost
                )
                update_withdrawable_cash = (
                    account[Accounts.withdrawable_cash.name] + order_cost
                )
                update_stock_value = account[Accounts.stock_value.name] - order_cost
                update_receiving_amount = (
                    account[Accounts.receiving_amount.name] - order_cost
                )
                await AccountsRepo.update(
                    record={
                        Accounts.id.name: pending_order["account_id"],
                        Accounts.available_cash.name: update_available_cash,
                        Accounts.withdrawable_cash.name: update_withdrawable_cash,
                        Accounts.receiving_amount.name: update_receiving_amount,
                        Accounts.stock_value.name: update_stock_value,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                )
