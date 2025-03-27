import asyncio

from src.modules.users.entities import Users
from src.modules.auth.services import AuthService
from src.modules.users.services import UserService
from src.modules.auth.dtos import RegisterDTO, LoginDTO
from src.modules.auth.types import JwtPayload, RefreshPayload
from src.utils.time_utils import TimeUtils


async def test_register():
    # account = await UserService.get_account("admin_user")
    register_payload = RegisterDTO(
        account="ltduong6124",
        password="asd123456",
        confirm_password="asd123456",
        role="admin",
        type_broker="",
        type_client="",
    )
    await AuthService.register(payload=register_payload)


async def test_login():
    login_payload = LoginDTO(account="ltduong6124", password="asd123456")
    token_pair = await AuthService.login(payload=login_payload)
    print(token_pair)


async def test_logout():
    logout_payload = JwtPayload(
        sessionId="8b33c1d2-d4dd-4843-a43c-6adce97d223e", userId=2, role="admin"
    )
    await AuthService.logout(payload=logout_payload)


async def test_rf_token():
    rf_payload = RefreshPayload(
        sessionId="045947c0-a238-4714-90e4-11775aaaee12",
        userId=2,
        role="admin",
        signature="23147ad49937d71725ec68cd21bed0b",
    )
    token_pair = await AuthService.refresh_token(payload=rf_payload)
    print(token_pair)


async def test_verify_access_token():
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiIyNTEzZTI2ZS0zYjQzLTRlZmEtOWNjYy0yNjU4NDdiNzE1NTUiLCJ1c2VySWQiOjUsInJvbGUiOiJhZG1pbiIsImlhdCI6MTc0MzA2NDMyNSwiZXhwIjoxNzQzMDY3OTI1fQ.ZHfQ_dOylPAhtlrphqTRS1DFmYP8GSWWe8qLQqSx9Vo"
    await AuthService.verify_access_token(access_token=access_token)



if __name__ == "__main__":
    # asyncio.run(test_register())
    # asyncio.run(test_login())
    # asyncio.run(test_logout())
    # asyncio.run(test_rf_token())
    asyncio.run(test_verify_access_token())
    # print(TimeUtils.get_current_vn_time())
