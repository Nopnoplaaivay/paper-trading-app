import asyncio
from src.modules.users.services import UserService


async def test_service():
    account = await UserService.get_account("admin_user")
    print(account)


if __name__ == "__main__":
    asyncio.run(test_service())