from backend.modules.dnse.realtime_data_provider import RealtimeDataProvider
from backend.common.responses.exceptions import BaseExceptionResponse

from backend.common.consts import SQLServerConsts
from backend.modules.base.query_builder import TextSQL
from backend.modules.investors.entities import Accounts, Transactions, Holdings
from backend.modules.investors.repositories import AccountsRepo, TransactionsRepo, HoldingsRepo
from backend.modules.users.entities import Users
from backend.modules.users.repositories import UsersRepo
from backend.modules.orders.entities import Orders
from backend.modules.orders.repositories import OrdersRepo
from backend.modules.orders.processors import OrdersProcessors
from backend.common.consts import MessageConsts


class AdminService:
    repo = UsersRepo
    orders_repo = OrdersRepo

    @classmethod
    async def get_all_users(cls):
        records = await cls.repo.get_all()
        return records

    @classmethod
    async def update_user(cls, payload):
        user = await cls.repo.get_by_id(payload.user_id)
        if not user:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="User not found"
            )
        updated_user = await cls.repo.update(
            record={
                Users.id.name: payload.user_id,
                Users.role.name: payload.role
            },
            identity_columns=[Users.id.name],
            text_clauses={"__updated_at__": TextSQL(SQLServerConsts.GMT_7_NOW_VARCHAR)},
            returning=True
        )
        return updated_user

    @classmethod
    async def get_all_orders(cls):
        orders = await cls.orders_repo.get_all()
        return orders

    @classmethod
    async def cancel_order(cls, payload):
        order = (await cls.orders_repo.get_by_id(payload.order_id))[0]
        if not order:
            return False
        if order[Orders.status.name] == "PENDING":
            await OrdersProcessors.update_on_cancel(order=order)
            return True
        return False