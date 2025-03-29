from src.common.responses.exceptions import BaseExceptionResponse
from src.modules.accounts.entities import Accounts, Transactions
from src.modules.accounts.repositories import AccountsRepo, TransactionsRepo
from src.modules.accounts.dtos import DepositDTO, WithdrawDTO
from src.modules.auth.types import JwtPayload
from src.common.consts import MessageConsts
from src.utils.time_utils import TimeUtils


class AccountsService:
    repo = AccountsRepo

    @classmethod
    async def get_balance(cls, payload: JwtPayload):
        conditions = {Accounts.user_id.name: payload.userId}
        records = await cls.repo.get_by_condition(conditions)
        if records:
            return records[0]
        else:
            return None

    @classmethod
    async def deposit(cls, payload: DepositDTO):
        conditions = {Accounts.id.name: payload.account_id}
        amount = payload.amount
        records = await cls.repo.get_by_condition(conditions)
        if records:
            record = records[0]
            total_cash = record[Accounts.total_cash.name] + amount
            available_cash = record[Accounts.available_cash.name] + amount
            withdrawable_cash = record[Accounts.withdrawable_cash.name] + amount
            net_asset_value = record[Accounts.net_asset_value.name] + amount
            purchasing_power = record[Accounts.purchasing_power.name] + amount
            updated_account = await cls.repo.update(
                record={
                    Accounts.id.name: record[Accounts.id.name],
                    Accounts.total_cash.name: total_cash,
                    Accounts.available_cash.name: available_cash,
                    Accounts.withdrawable_cash.name: withdrawable_cash,
                    Accounts.net_asset_value.name: net_asset_value,
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
                    Transactions.payment_method.name: payload.payment_method,
                    Transactions.created_at.name: TimeUtils.get_current_vn_time(),
                },
                returning=False,
            )
            return updated_account
        else:
            return None

    @classmethod
    async def withdraw(cls, payload: WithdrawDTO):
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
            current_withdrawable_cash = record[Accounts.withdrawable_cash.name]
            if current_withdrawable_cash < amount:
                raise BaseExceptionResponse(
                    http_code=400,
                    status_code=400,
                    message=MessageConsts.BAD_REQUEST,
                    errors="Exceed withdrawable cash",
                )

            total_cash = record[Accounts.total_cash.name] - amount
            available_cash = record[Accounts.available_cash.name] - amount
            withdrawable_cash = record[Accounts.withdrawable_cash.name] - amount
            net_asset_value = record[Accounts.net_asset_value.name] - amount
            purchasing_power = record[Accounts.purchasing_power.name] - amount
            updated_account = await cls.repo.update(
                record={
                    Accounts.id.name: record[Accounts.id.name],
                    Accounts.total_cash.name: total_cash,
                    Accounts.available_cash.name: available_cash,
                    Accounts.withdrawable_cash.name: withdrawable_cash,
                    Accounts.net_asset_value.name: net_asset_value,
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
                    Transactions.payment_method.name: payload.payment_method,
                    Transactions.created_at.name: TimeUtils.get_current_vn_time(),
                },
                returning=False,
            )
            return updated_account
        else:
            return None