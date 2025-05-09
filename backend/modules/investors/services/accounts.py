from backend.modules.dnse.realtime_data_provider import RealtimeDataProvider
from backend.common.responses.exceptions import BaseExceptionResponse
from backend.modules.investors.entities import Accounts, Transactions, Holdings
from backend.modules.investors.repositories import AccountsRepo, TransactionsRepo, HoldingsRepo
from backend.modules.investors.dtos import DepositDTO, WithdrawDTO
from backend.modules.auth.types import JwtPayload
from backend.common.consts import MessageConsts


class AccountsService:
    repo = AccountsRepo

    @classmethod
    async def get_balance(cls, payload: JwtPayload):
        conditions = {Accounts.user_id.name: payload.userId}
        records = await cls.repo.get_by_condition(conditions=conditions)
        balance = {
            "nav": 0,
            "available_cash": 0,
            "stock_value": 0,
            "purchasing_power": 0,
            "securing_amount": 0,
        }
        if records:
            record = records[0]
            balance["available_cash"] = record[Accounts.available_cash.name]
            balance["securing_amount"] = record[Accounts.securing_amount.name]
            balance["purchasing_power"] = record[Accounts.purchasing_power.name]

            holdings = await HoldingsRepo.get_by_condition(
                {Holdings.account_id.name: record[Accounts.id.name]},
            )
            if holdings:
                for holding in holdings:
                    current_price = RealtimeDataProvider.get_market_price(symbol=holding[Holdings.symbol.name])
                    balance["stock_value"] += current_price * holding[Holdings.quantity.name]

            balance["nav"] = balance["available_cash"] + balance["securing_amount"] + balance["stock_value"]
        return balance

    @classmethod
    async def deposit(cls, payload: DepositDTO, user: JwtPayload):
        conditions = {Accounts.id.name: payload.account_id}
        amount = payload.amount
        if amount <= 0:
            raise BaseExceptionResponse(
                http_code=400,
                status_code=400,
                message=MessageConsts.BAD_REQUEST,
                errors="Amount must be greater than zero",
            )
        records = await cls.repo.get_by_condition(conditions)
        if records:
            record = records[0]
            if record[Accounts.user_id.name] != user.userId:
                raise BaseExceptionResponse(
                    http_code=403,
                    status_code=403,
                    message=MessageConsts.FORBIDDEN,
                    errors="You do not have permission to this account",
                )
            available_cash = record[Accounts.available_cash.name] + amount
            purchasing_power = record[Accounts.purchasing_power.name] + amount
            updated_account = await cls.repo.update(
                record={
                    Accounts.id.name: record[Accounts.id.name],
                    Accounts.available_cash.name: available_cash,
                    Accounts.purchasing_power.name: purchasing_power,
                },
                identity_columns=[Accounts.id.name],
                returning=True,
            )
            await TransactionsRepo.insert(
                record={
                    Transactions.account_id.name: payload.account_id,
                    Transactions.transaction_type.name: "deposit",
                    Transactions.amount.name: amount,
                    Transactions.payment_method.name: payload.payment_method
                },
                returning=False,
            )
            return updated_account
        else:
            return None

    @classmethod
    async def withdraw(cls, payload: WithdrawDTO, user: JwtPayload):
        conditions = {Accounts.id.name: payload.account_id}
        amount = payload.amount
        if amount <= 0:
            raise BaseExceptionResponse(
                http_code=400,
                status_code=400,
                message=MessageConsts.BAD_REQUEST,
                errors="Amount must be greater than zero",
            )
        records = await cls.repo.get_by_condition(conditions)
        if records:
            record = records[0]
            if record[Accounts.user_id.name] != user.userId:
                raise BaseExceptionResponse(
                    http_code=403,
                    status_code=403,
                    message=MessageConsts.FORBIDDEN,
                    errors="You do not have permission to this account",
                )
            current_withdrawable_cash = record[Accounts.withdrawable_cash.name]
            if current_withdrawable_cash < amount:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.BAD_REQUEST,
                    errors="Exceed withdrawable cash",
                )

            available_cash = record[Accounts.available_cash.name] - amount
            purchasing_power = record[Accounts.purchasing_power.name] - amount
            updated_account = await cls.repo.update(
                record={
                    Accounts.id.name: record[Accounts.id.name],
                    Accounts.available_cash.name: available_cash,
                    Accounts.purchasing_power.name: purchasing_power,
                },
                identity_columns=[Accounts.id.name],
                returning=True,
            )
            await TransactionsRepo.insert(
                record={
                    Transactions.account_id.name: payload.account_id,
                    Transactions.transaction_type.name: "withdraw",
                    Transactions.amount.name: amount,
                    Transactions.payment_method.name: payload.payment_method
                },
                returning=False,
            )
            return updated_account
        else:
            return None