from uuid import uuid4

from src.common.consts import SQLServerConsts
from src.cache.connector import REDIS_POOL
from src.cache.config import OrdersConfigs
from src.modules.base.query_builder import TextSQL
from src.common.responses.exceptions import BaseExceptionResponse
from src.modules.investors.entities import Accounts, Holdings
from src.modules.investors.repositories import AccountsRepo, HoldingsRepo
from src.modules.orders.entities import Orders, MatchOrders
from src.modules.orders.repositories import OrdersRepo, MatchOrdersRepo

from src.utils.logger import LOGGER

class OrdersProcessors:
    redis_conn = REDIS_POOL.get_conn()

    @classmethod
    async def update_on_pending(cls, order):
        order_key = f"{OrdersConfigs.KEY_PENDING_ORDERS}:{order['symbol']}:{order['id']}"
        cls.redis_conn.hset(order_key, mapping=order)

        if order["side"] == "SIDE_BUY":
            async with AccountsRepo.session_scope() as session:
                conditions = {Accounts.id.name: order[Orders.account_id.name]}
                account = (await AccountsRepo.get_by_condition(conditions=conditions))[0]

                update_available_cash = account["available_cash"] - order["quantity"] * order["price"]
                update_purchasing_power = account["purchasing_power"] - order["quantity"] * order["price"]
                update_securing_amount = account["securing_amount"] + order["quantity"] * order["price"]

                await AccountsRepo.update(
                    record={
                        Accounts.id.name: account["id"],
                        Accounts.available_cash.name: update_available_cash,
                        Accounts.purchasing_power.name: update_purchasing_power,
                        Accounts.securing_amount.name: update_securing_amount,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                )
                await session.commit()
        elif order["side"] == "SIDE_SELL":
            async with HoldingsRepo.session_scope() as session:
                conditions = {
                    Holdings.account_id.name: order[Orders.account_id.name],
                    Holdings.symbol.name: order[Orders.symbol.name],
                }
                holding = (await HoldingsRepo.get_by_condition(conditions=conditions))[0]

                update_locked_quantity = holding[Holdings.locked_quantity.name] + order[Orders.quantity.name]

                await HoldingsRepo.update(
                    record={
                        Holdings.id.name: holding[Holdings.id.name],
                        Holdings.locked_quantity.name: update_locked_quantity,
                    },
                    identity_columns=[Holdings.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                )
                await session.commit()

        await OrdersRepo.insert(
            record=order,
            returning=False,
        )

    @classmethod
    async def update_on_complete(cls, order):
        """Update order on complete"""
        order_key = f"{OrdersConfigs.KEY_PENDING_ORDERS}:{order['symbol']}:{order['id']}"
        cls.redis_conn.delete(order_key)

        if order["side"] == "SIDE_BUY":
            async with AccountsRepo.session_scope() as session:
                conditions = {Accounts.id.name: order[Orders.account_id.name]}
                account = (await AccountsRepo.get_by_condition(conditions=conditions))[0]

                update_securing_amount = account["securing_amount"] - order["quantity"] * order["price"]
                await AccountsRepo.update(
                    record={
                        Accounts.id.name: account["id"],
                        Accounts.securing_amount.name: update_securing_amount,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                )
                await session.commit()
            async with HoldingsRepo.session_scope() as session:
                conditions = {
                    Holdings.account_id.name: order[Orders.account_id.name],
                    Holdings.symbol.name: order[Orders.symbol.name],
                }
                holdings = await HoldingsRepo.get_by_condition(conditions=conditions)
                if holdings:
                    holding = holdings[0]
                    update_quantity = holding[Holdings.quantity.name] + order[Orders.quantity.name]
                    update_cost_basis_per_share = (
                        holding[Holdings.cost_basis_per_share.name] * holding[Holdings.quantity.name]
                        + order[Orders.price.name] * order[Orders.quantity.name]
                    ) / update_quantity

                    await HoldingsRepo.update(
                        record={
                            Holdings.id.name: holding[Holdings.id.name],
                            Holdings.quantity.name: update_quantity,
                            Holdings.cost_basis_per_share.name: update_cost_basis_per_share,
                        },
                        identity_columns=[Holdings.id.name],
                        returning=False,
                        text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                    )
                    await session.commit()
                else:
                    await HoldingsRepo.insert(
                        record={
                            Holdings.account_id.name: order[Orders.account_id.name],
                            Holdings.symbol.name: order[Orders.symbol.name],
                            Holdings.price.name: order[Orders.price.name],
                            Holdings.quantity.name: order[Orders.quantity.name],
                            Holdings.cost_basis_per_share.name: order[Orders.price.name],
                        },
                        returning=False,
                    )
                    await session.commit()
            LOGGER.info(f"Order {order['id']} MATCHED. Account {order['account_id']} has bought {order['quantity']} shares of {order['symbol']} at {order['price']}.")

        elif order["side"] == "SIDE_SELL":
            async with AccountsRepo.session_scope() as session:
                conditions = {Accounts.id.name: order[Orders.account_id.name]}
                account = (await AccountsRepo.get_by_condition(conditions=conditions))[0]

                update_available_cash = account["available_cash"] + order["quantity"] * order["price"]
                update_purchasing_power = account["purchasing_power"] + order["quantity"] * order["price"]
                update_securing_amount = account["securing_amount"] - order["quantity"] * order["price"]

                await AccountsRepo.update(
                    record={
                        Accounts.id.name: account["id"],
                        Accounts.available_cash.name: update_available_cash,
                        Accounts.purchasing_power.name: update_purchasing_power,
                        Accounts.securing_amount.name: update_securing_amount,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                )
                await session.commit()
            async with HoldingsRepo.session_scope() as session:
                conditions = {
                    Holdings.account_id.name: order[Orders.account_id.name],
                    Holdings.symbol.name: order[Orders.symbol.name],
                }
                holding = (await HoldingsRepo.get_by_condition(conditions=conditions))[0]

                update_quantity = holding[Holdings.quantity.name] - order[Orders.quantity.name]
                update_locked_quantity = holding[Holdings.locked_quantity.name] - order[Orders.quantity.name]

                await HoldingsRepo.update(
                    record={
                        Holdings.id.name: holding[Holdings.id.name],
                        Holdings.quantity.name: update_quantity,
                        Holdings.locked_quantity.name: update_locked_quantity,
                    },
                    identity_columns=[Holdings.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                )
                await session.commit()

            LOGGER.info(f"Order {order['id']} MATCHED. Account {order['account_id']} has sold {order['quantity']} shares of {order['symbol']} at {order['price']}.")

        await OrdersRepo.update(
            record={
                Orders.id.name: order[Orders.id.name],
                Orders.status.name: "COMPLETE",
            },
            identity_columns=[Orders.id.name],
            returning=False,
            text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
        )

        await MatchOrdersRepo.insert(
            record={
                MatchOrders.account_id.name: order[Orders.account_id.name],
                MatchOrders.order_id.name: order[Orders.id.name],
                MatchOrders.symbol.name: order[Orders.symbol.name],
                MatchOrders.price.name: order[Orders.price.name],
                MatchOrders.quantity.name: order[Orders.quantity.name],
                MatchOrders.side.name: order[Orders.side.name],
                MatchOrders.order_type.name: order[Orders.order_type.name],
                MatchOrders.total_amount.name: order[Orders.price.name] * order[Orders.quantity.name],
            },
            returning=False
        )


    @classmethod
    async def update_on_cancel(cls, order):
        """Update order on cancel"""
        order_key = f"{OrdersConfigs.KEY_PENDING_ORDERS}:{order['symbol']}:{order['id']}"
        cls.redis_conn.delete(order_key)

        if order["side"] == "SIDE_BUY":
            async with AccountsRepo.session_scope() as session:
                conditions = {Accounts.id.name: order[Orders.account_id.name]}
                account = (await AccountsRepo.get_by_condition(conditions=conditions))[0]

                update_available_cash = account["available_cash"] + order["quantity"] * order["price"]
                update_purchasing_power = account["purchasing_power"] + order["quantity"] * order["price"]
                update_securing_amount = account["securing_amount"] - order["quantity"] * order["price"]

                await AccountsRepo.update(
                    record={
                        Accounts.id.name: account["id"],
                        Accounts.available_cash.name: update_available_cash,
                        Accounts.purchasing_power.name: update_purchasing_power,
                        Accounts.securing_amount.name: update_securing_amount,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},

                )
                await session.commit()

            await OrdersRepo.update(
                record={
                    Orders.id.name: order[Orders.id.name],
                    Orders.status.name: "CANCELED",
                },
                identity_columns=[Orders.id.name],
                returning=False,
                text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
            )
        elif order["side"] == "SIDE_SELL":
            async with HoldingsRepo.session_scope() as session:
                conditions = {
                    Holdings.account_id.name: order[Orders.account_id.name],
                    Holdings.symbol.name: order[Orders.symbol.name],
                }
                holding = (await HoldingsRepo.get_by_condition(conditions=conditions))[0]

                update_locked_quantity = holding[Holdings.locked_quantity.name] - order[Orders.quantity.name]

                await HoldingsRepo.update(
                    record={
                        Holdings.id.name: holding[Holdings.id.name],
                        Holdings.locked_quantity.name: update_locked_quantity,
                    },
                    identity_columns=[Holdings.id.name],
                    returning=False,
                    text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
                )
                await session.commit()

            await OrdersRepo.update(
                record={
                    Orders.id.name: order[Orders.id.name],
                    Orders.status.name: "CANCELLED",
                },
                identity_columns=[Orders.id.name],
                returning=False,
                text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
            )