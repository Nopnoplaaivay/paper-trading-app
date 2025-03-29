from src.common.responses.exceptions import BaseExceptionResponse
from src.modules.accounts.entities import Accounts
from src.modules.accounts.repositories import AccountsRepo
from src.modules.orders.entities import Orders
from src.modules.orders.repositories import OrdersRepo
from src.modules.orders.dtos import OrdersDTO, PowerDTO, PowerResponseDTO
from src.common.consts import MessageConsts
from src.utils.time_utils import TimeUtils


class OrdersService:
    repo = OrdersRepo

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
            power = {
                "account_id": account_id,
                "ppse": ppse,
                "pp_total": pp_total,
                "qmax": qmax,
                "qmax_long": qmax_long,
                "qmax_short": qmax_short,
                "trade_quantity": trade_quantity,
                "price": price,
            }
            return power
        else:
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message=MessageConsts.NOT_FOUND,
                errors="Account not found",
            )


