from src.cache import OrderCache
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
            if payload.side == OrderSide.SELL.value:
                if not securities:
                    raise BaseExceptionResponse(
                        http_code=404,
                        status_code=404,
                        message=MessageConsts.NOT_FOUND,
                        errors="Account does not have this security",
                    )
                security = securities[0]
                if security[Portfolios.quantity.name] < payload.order_quantity:
                    raise BaseExceptionResponse(
                        http_code=400,
                        status_code=400,
                        message=MessageConsts.INVALID_INPUT,
                        errors="Exceeding quantity of securities in account",
                    ) 
            elif payload.side == OrderSide.BUY.value:
                """Update account balance"""
                order_cost = payload.price * payload.order_quantity
                securing_amount = account[Accounts.securing_amount.name] + order_cost
                total_cash = account[Accounts.total_cash.name] - order_cost
                available_cash = account[Accounts.available_cash.name] - order_cost
                withdrawable_cash = account[Accounts.withdrawable_cash.name] - order_cost
                purchasing_power = account[Accounts.purchasing_power.name] - order_cost
                vn_current_time = TimeUtils.get_current_vn_time()
                await AccountsRepo.update(
                    record={
                        Accounts.id.name: payload.account_id,
                        Accounts.total_cash.name: total_cash,
                        Accounts.purchasing_power.name: purchasing_power,
                        Accounts.available_cash.name: available_cash,
                        Accounts.withdrawable_cash.name: withdrawable_cash,
                        Accounts.securing_amount.name: securing_amount
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                )
            elif payload.side == OrderSide.SELL.value:
                order_cost = payload.price * payload.order_quantity
                receiving_amount = account[Accounts.receiving_amount.name] + order_cost
                stock_value = account[Accounts.stock_value.name] - receiving_amount
                await AccountsRepo.update(
                    record={
                        Accounts.id.name: payload.account_id,
                        Accounts.stock_value.name: stock_value,
                        Accounts.receiving_amount.name: receiving_amount,
                    },
                    identity_columns=[Accounts.id.name],
                    returning=False,
                )

            """Insert order into DB"""
            new_order = await cls.repo.insert(
                record={
                    Orders.account_id.name: payload.account_id,
                    Orders.side.name: payload.side,
                    Orders.symbol.name: payload.symbol,
                    Orders.price.name: payload.price,
                    Orders.order_type.name: payload.order_type,
                    Orders.order_quantity.name: payload.order_quantity,
                    Orders.order_status.name: OrderStatus.PENDING.value,
                    Orders.filled_quantity.name: 0,
                    Orders.last_quantity.name: 0,
                    Orders.error.name: "",
                    Orders.created_at.name: vn_current_time,
                    Orders.updated_at.name: vn_current_time,
                },
                returning=True
            )

            # Add order to Redis cache
            new_order["created_at"] = new_order["created_at"].strftime(SQLServerConsts.TRADING_TIME_FORMAT)
            new_order["updated_at"] = new_order["updated_at"].strftime(SQLServerConsts.TRADING_TIME_FORMAT)
            
            await OrderCache.add_order(new_order)
            return new_order    
        else:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Account not found",
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


