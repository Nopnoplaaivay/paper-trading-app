from uuid import uuid4

from src.cache import OrdersCache, TickCache
from src.common.consts import SQLServerConsts
from src.common.responses.exceptions import BaseExceptionResponse
from src.modules.accounts.entities import Accounts, Securities
from src.modules.accounts.repositories import AccountsRepo, SecuritiesRepo
from src.modules.orders.entities import Orders, OrderStatus, OrderSide
from src.modules.orders.repositories import OrdersRepo
from src.modules.orders.dtos import (
    OrdersDTO, 
    PowerDTO, 
    PowerResponseDTO, 
    OrdersResponseDTO
)
from src.modules.auth.types import JwtPayload
from src.common.consts import MessageConsts
from src.utils.time_utils import TimeUtils


class OrdersService:
    repo = OrdersRepo

    @classmethod
    async def place_order(cls, payload: OrdersDTO, user: JwtPayload):
        """Validate account"""
        account = await cls.validate_order(payload=payload, user=user)
        """
        Check matching order
        If match, insert order to database and update account balance
        If not, insert order to cache and wait for matching
        """
        record = {
            Orders.id.name: str(uuid4()).upper(),
            Orders.account_id.name: payload.account_id,
            Orders.side.name: payload.side,
            Orders.symbol.name: payload.symbol,
            Orders.price.name: payload.price,
            Orders.order_type.name: payload.order_type,
            Orders.qtty.name: payload.qtty,
            Orders.error.name: "",
        }
        if payload.side == OrderSide.BUY.value:
            match_price = await TickCache.get_match_price(symbol=payload.symbol)
            if payload.price == match_price:
                record[Orders.status.name] = OrderStatus.COMPLETED.value
                record = await cls.repo.insert(record=record, returning=True)
            else:
                record[Orders.status.name] = OrderStatus.PENDING.value
                record["created_at"] = TimeUtils.get_current_vn_time().strftime(
                    SQLServerConsts.TRADING_TIME_FORMAT
                )
                await OrdersCache.add(order=record)
        elif payload.side == OrderSide.SELL.value:
            match_price = await TickCache.get_match_price(symbol=payload.symbol)
            if payload.price == match_price:
                record[Orders.status.name] = OrderStatus.COMPLETED.value
                record = await cls.repo.insert(record=record, returning=True)
            else:
                record[Orders.status.name] = OrderStatus.PENDING.value
                record["created_at"] = TimeUtils.get_current_vn_time().strftime(
                    SQLServerConsts.TRADING_TIME_FORMAT
                )
                await OrdersCache.add(order=record)

        return OrdersResponseDTO(
            id=record[Orders.id.name],
            side=record[Orders.side.name],
            symbol=record[Orders.symbol.name],
            price=record[Orders.price.name],
            qtty=record[Orders.qtty.name],
            order_type=record[Orders.order_type.name],
            status=record[Orders.status.name]
        ).model_dump()

        """Update account balance"""


    @classmethod
    async def validate_order(cls, payload: OrdersDTO, user: JwtPayload):
        conditions = {Accounts.id.name: payload.account_id}
        records = await AccountsRepo.get_by_condition(conditions)
        if records:
            account = records[0]
            if account[Accounts.user_id.name] != user.userId:
                raise BaseExceptionResponse(
                    http_code=403,
                    status_code=403,
                    message=MessageConsts.FORBIDDEN,
                    errors="You do not have permission to this account",
                )
            if account[Accounts.purchasing_power.name] < payload.price * payload.qtty:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="Not enough purchasing power",
                )
            if payload.qtty <= 0:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="Order quantity must be greater than 0",
                )
            if payload.price <= 0:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="Price must be greater than 0",
                )

            """Check security in portfolio"""
            securities = await SecuritiesRepo.get_by_condition(
                {
                    Securities.account_id.name: payload.account_id,
                    Securities.symbol.name: payload.symbol,
                }
            )
            if payload.side == "SIDE_SELL" and not securities:
                raise BaseExceptionResponse(
                    http_code=404,
                    status_code=404,
                    message=MessageConsts.NOT_FOUND,
                    errors="Account does not have this security",
                )
        else:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Account not found",
            )
        return account

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
