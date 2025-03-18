from src.modules.users.entities import Users
from src.modules.users.repositories import UsersRepo


class UserService:
    repo = UsersRepo

    @classmethod
    async def get_account(cls, account: str):
        conditions = {"account": account}
        records = await cls.repo.get_by_condition(conditions)
        if records:
            return records[0]
        else:
            return None