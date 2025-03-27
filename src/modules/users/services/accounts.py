from src.modules.users.entities import Accounts
from src.modules.users.repositories import AccountsRepo


class AccountsService:
    repo = AccountsRepo

    @classmethod
    async def get_balance(cls, user_id: str):
        conditions = {"user_id": user_id}
        records = await cls.repo.get_by_condition(conditions)
        if records:
            return records[0]
        else:
            return None