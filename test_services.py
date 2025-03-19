import asyncio

from src.modules.users.entities import Users
from src.modules.auth.services import AuthService
from src.modules.users.services import UserService
from src.modules.auth.dtos import RegisterDTO, LoginDTO
from src.utils.time_utils import TimeUtils

async def test_register():
    # account = await UserService.get_account("admin_user")
    register_payload = RegisterDTO(
        account="khang",
        password="asd123456",
        confirm_password="asd123456",
        role="admin",
        type_broker="",
        type_client=""
    )
    await AuthService.register(payload=register_payload)

async def test_login():
    login_payload = LoginDTO(
        account="khang",
        password="asd123456"
    )
    token_pair = await AuthService.login(payload=login_payload)
    print(token_pair)

if __name__ == "__main__":
    asyncio.run(test_login())