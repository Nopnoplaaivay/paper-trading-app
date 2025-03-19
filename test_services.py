import asyncio

from src.modules.users.entities import Users
from src.modules.auth.services import AuthService
from src.modules.users.services import UserService
from src.modules.auth.dtos import RegisterDTO

async def test_service():
    # account = await UserService.get_account("admin_user")
    register_dto = RegisterDTO(
        account="khang",
        password="asd123456",
        confirm_password="asd123456",
        role="admin",
        type_broker="",
        type_client=""
    )
    await AuthService.register(payload=register_dto)


if __name__ == "__main__":
    asyncio.run(test_service())