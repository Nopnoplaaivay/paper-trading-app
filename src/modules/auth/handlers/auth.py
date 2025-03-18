from fastapi import Depends

from src.common.consts import MessageConsts
from src.common.responses.base import BaseResponse
from src.modules.auth.dtos import RegisterDTO, LoginDTO
from src.modules.auth.handlers import auth_router


@auth_router.post("/register")
async def register(payload: RegisterDTO):
    pass

@auth_router.post("/login")
async def login(payload: LoginDTO):
    pass

@auth_router.get("/logout")
async def logout():
    pass