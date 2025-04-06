from uuid import uuid4

from src.redis import OrdersCache, TickCache
from src.common.consts import SQLServerConsts
from src.common.responses.exceptions import BaseExceptionResponse
from src.modules.accounts.entities import Accounts, Portfolios
from src.modules.accounts.repositories import AccountsRepo, PortfoliosRepo
from src.modules.orders.entities import Orders, OrderStatus, OrderSide
from src.modules.orders.repositories import OrdersRepo
from src.modules.orders.dtos import OrdersDTO, PowerDTO, PowerResponseDTO
from src.modules.auth.types import JwtPayload
from src.common.consts import MessageConsts
from src.utils.time_utils import TimeUtils


class OrdersService:
    repo = OrdersRepo

    @classmethod
    async def place_order(cls, payload: OrdersDTO, user: JwtPayload):
        """Validate account"""
        account = await cls.validate_order(payload=payload, user=user)
        vn_current_time = TimeUtils.get_current_vn_time()

        new_order = {
            Orders.id.name: str(uuid4()),
            Orders.account_id.name: payload.account_id,
            Orders.side.name: payload.side,
            Orders.symbol.name: payload.symbol,
            Orders.price.name: payload.price,
            Orders.order_type.name: payload.order_type,
            Orders.qtty.name: payload.order_quantity,
            Orders.status.name: "PENDING",
            "created_at": vn_current_time.strftime(SQLServerConsts.TRADING_TIME_FORMAT),
            "updated_at": vn_current_time.strftime(SQLServerConsts.TRADING_TIME_FORMAT),
        }
        
        await OrdersCache.add(order=new_order)
        return new_order    

        """Update account balance"""
        # if payload.side == "SIDE_SELL":
        #     order_cost = payload.price * payload.order_quantity
        #     receiving_amount = account[Accounts.receiving_amount.name] + order_cost
        #     stock_value = account[Accounts.stock_value.name] - receiving_amount
        #     await AccountsRepo.update(
        #         record={
        #             Accounts.id.name: payload.account_id,
        #             Accounts.stock_value.name: stock_value,
        #             Accounts.receiving_amount.name: receiving_amount,
        #         },
        #         identity_columns=[Accounts.id.name],
        #         returning=False,
        #     )
        # elif payload.side == "SIDE_BUY":
        #     """Update account balance"""
        #     order_cost = payload.price * payload.order_quantity
        #     securing_amount = account[Accounts.securing_amount.name] + order_cost
        #     total_cash = account[Accounts.total_cash.name] - order_cost
        #     available_cash = account[Accounts.available_cash.name] - order_cost
        #     withdrawable_cash = account[Accounts.withdrawable_cash.name] - order_cost
        #     purchasing_power = account[Accounts.purchasing_power.name] - order_cost
        #     vn_current_time = TimeUtils.get_current_vn_time()
        #     await AccountsRepo.update(
        #         record={
        #             Accounts.id.name: payload.account_id,
        #             Accounts.total_cash.name: total_cash,
        #             Accounts.purchasing_power.name: purchasing_power,
        #             Accounts.available_cash.name: available_cash,
        #             Accounts.withdrawable_cash.name: withdrawable_cash,
        #             Accounts.securing_amount.name: securing_amount
        #         },
        #         identity_columns=[Accounts.id.name],
        #         returning=False,
        #     )

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
            if account[Accounts.purchasing_power.name] < payload.price * payload.order_quantity:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.INVALID_INPUT,
                    errors="Not enough purchasing power",
                )
            if payload.order_quantity <= 0:
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
            securities = await PortfoliosRepo.get_by_condition(
                {Portfolios.account_id.name: payload.account_id, Portfolios.symbol.name: payload.symbol}
            )
            if payload.side == "SIDE_SELL" and not securities:
                raise BaseExceptionResponse(
                    http_code=404,
                    status_code=404,
                    message=MessageConsts.NOT_FOUND,
                    errors="Account does not have this stock",
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
            qmax_short = 0 # fix after create portfolio
            trade_quantity = 0 # fix after create portfolio
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


