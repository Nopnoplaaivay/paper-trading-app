import datetime
from uuid import uuid4

from backend.cache.connector import REDIS_POOL
from backend.cache.config import OrdersConfigs
from backend.common.responses.exceptions import BaseExceptionResponse
from backend.modules.dnse.realtime_data_provider import RealtimeDataProvider
from backend.modules.investors.entities import Accounts, Holdings
from backend.modules.investors.repositories import AccountsRepo, HoldingsRepo
from backend.modules.orders.entities import Orders
from backend.modules.orders.repositories import OrdersRepo
from backend.modules.orders.processors import OrdersProcessors
from backend.modules.orders.dtos import (
    OrdersDTO,
    OrdersCancelDTO,
    PowerDTO, 
    PowerResponseDTO, 
    OrdersResponseDTO
)
from backend.modules.auth.types import JwtPayload
from backend.common.consts import MessageConsts
from backend.utils.time_utils import TimeUtils


class OrdersService:
    repo = OrdersRepo

    @classmethod
    async def place_order(cls, payload: OrdersDTO, user: JwtPayload):
        try:
            """Check user permission"""
            account = (await AccountsRepo.get_by_condition(conditions={Accounts.id.name: payload.account_id}))[0]
            if account[Accounts.user_id.name] != user.userId:
                raise BaseExceptionResponse(
                    http_code=403,
                    status_code=403,
                    message=MessageConsts.FORBIDDEN,
                    errors="You do not have permission to this account",
                )

            """Check input"""
            if payload.side not in ["SIDE_BUY", "SIDE_SELL"]:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="INVALID_ORDER_SIDE",
                )
            if payload.order_type not in ["LO", "MP"]:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="INVALID_ORDER_TYPE",
                )

            """Check price/quantity input"""
            if payload.order_type == "LO" and payload.price <= 0:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="INVALID_PRICE_LOT",
                )
            if payload.qtty <= 0:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="INVALID_QUANTITY_LOT",
                )

            if payload.order_type == "MP":
                current_price = RealtimeDataProvider.get_market_price(payload.symbol)
                if current_price is None:
                    raise BaseExceptionResponse(
                        http_code=404,
                        status_code=404,
                        message=MessageConsts.NOT_FOUND,
                        errors="MARKET_PRICE_NOT_FOUND",
                    )
                payload.price = current_price

            """Check purchasing power"""
            if payload.side == "SIDE_BUY":
                if payload.price * payload.qtty > account[Accounts.purchasing_power.name]:
                    raise BaseExceptionResponse(
                        http_code=400,
                        status_code=400,
                        message=MessageConsts.INVALID_INPUT,
                        errors="QUANTITY_EXCEEDS_PURCHASING_POWER",
                    )
            if payload.side == "SIDE_SELL":
                """Check security in portfolio"""
                conditions = {
                    Holdings.account_id.name: payload.account_id,
                    Holdings.symbol.name: payload.symbol,
                }
                holdings = await HoldingsRepo.get_by_condition(conditions=conditions)
                if not holdings:
                    raise BaseExceptionResponse(
                        http_code=404,
                        status_code=404,
                        message=MessageConsts.NOT_FOUND,
                        errors="SECURITY_NOT_FOUND_IN_PORTFOLIO",
                    )
                else:
                    holding = holdings[0]
                    if holding[Holdings.quantity.name] - holding[Holdings.locked_quantity.name] < payload.qtty:
                        raise BaseExceptionResponse(
                            http_code=400,
                            status_code=400,
                            message=MessageConsts.INVALID_INPUT,
                            errors="QUANTITY_EXCEEDS_HOLDING",
                        )

        except Exception as e:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Account not found",
            )

        """
        Check matching_engine order
        If match, insert order to database and update account balance
        If not, insert order to cache and wait for matching_engine
        """
        order = {
            Orders.id.name: str(uuid4()),
            Orders.account_id.name: payload.account_id,
            Orders.side.name: payload.side,
            Orders.symbol.name: payload.symbol,
            Orders.price.name: payload.price,
            Orders.order_type.name: payload.order_type,
            Orders.quantity.name: payload.qtty,
            Orders.error.name: "",
        }

        """Update order on pending"""
        await OrdersProcessors.update_on_pending(order=order)

        return OrdersResponseDTO(
            id=order[Orders.id.name],
            side=order[Orders.side.name],
            symbol=order[Orders.symbol.name],
            price=order[Orders.price.name],
            qtty=order[Orders.quantity.name],
            order_type=order[Orders.order_type.name],
        ).model_dump()

    @classmethod
    async def cancel_order(cls, payload: OrdersCancelDTO, user: JwtPayload):
        """Check user permission"""
        try:
            account = (await AccountsRepo.get_by_condition(conditions={Accounts.id.name: payload.account_id}))[0]
            if account[Accounts.user_id.name] != user.userId:
                raise BaseExceptionResponse(
                    http_code=403,
                    status_code=403,
                    message=MessageConsts.FORBIDDEN,
                    errors="You do not have permission to this account",
                )
        except Exception:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Account not found",
            )

        """Cancel order"""
        try:
            conditions = {
                Orders.id.name: payload.order_id,
                Orders.account_id.name: payload.account_id,
            }
            order = (await cls.repo.get_by_condition(conditions=conditions))[0]
            if order[Orders.status.name] == "PENDING":
                await OrdersProcessors.update_on_cancel(order=order)
            else:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="Order is not pending",
                )
        except Exception:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Order not found",
            )
        return True

    @classmethod
    async def get_orders(cls, payload: JwtPayload):
        """Check user permission"""
        try:
            conditions = {Accounts.user_id.name: payload.userId}
            records = await AccountsRepo.get_by_condition(conditions=conditions)
            if records:
                record = records[0]
                account_id = record[Accounts.id.name]
                conditions = {Orders.account_id.name: account_id}
                orders = await cls.repo.get_by_condition(conditions=conditions)

                today_orders = []
                for order in orders:
                    if datetime.datetime.strptime(order["__created_at__"], "%Y-%m-%d %H:%M:%S").date() == TimeUtils.get_current_vn_time().date():
                        today_orders.append(order)

                return today_orders
        except Exception as e:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors=str(e),
            )


    @classmethod
    async def get_power(cls, payload: PowerDTO):
        account_id = payload.account_id
        conditions = {Accounts.id.name: account_id}
        if payload.price <= 0:
            raise BaseExceptionResponse(
                http_code=400,
                status_code=400,
                message=MessageConsts.INVALID_INPUT,
                errors="Price must be greater than 0",
            )
        records = await AccountsRepo.get_by_condition(conditions)
        if records:
            account = records[0]
            price = payload.price
            qmax = account[Accounts.purchasing_power.name] // payload.price
            qmax_long = qmax
            qmax_short = 0  # fix after create portfolio
            trade_quantity = 0  # fix after create portfolio
            ppse = price * qmax
            pp_total = account[Accounts.purchasing_power.name]
            power = PowerResponseDTO(
                account_id=account_id,
                ppse=ppse,
                pp_total=pp_total,
                qmax=qmax,
                qmax_long=qmax_long,
                qmax_short=qmax_short,
                trade_quantity=trade_quantity,
                price=price,
            ).model_dump()
            return power
        else:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Account not found",
            )
