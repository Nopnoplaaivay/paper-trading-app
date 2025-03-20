from fastapi import Depends
from starlette.responses import JSONResponse

from src.common.consts import MessageConsts
from src.common.responses.base import BaseResponse
from src.common.responses import SuccessResponse
from src.modules.auth.dtos import RegisterDTO, LoginDTO, LogoutDTO, RefreshDTO
from src.modules.auth.handlers import auth_router
from src.modules.auth.services import AuthService

@auth_router.post("/register")
async def register(payload: RegisterDTO):
    await AuthService.register(payload=payload)
    return BaseResponse(http_code=200, status_code=200, message=MessageConsts.SUCCESS)

@auth_router.post("/login")
async def login(payload: LoginDTO):
    token_pair = await AuthService.login(payload=payload)
    response = SuccessResponse(http_code=200, status_code=200, message=MessageConsts.SUCCESS, data=token_pair)
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@auth_router.get("/logout")
async def logout(payload: LogoutDTO):
    await AuthService.logout(payload=payload)

@auth_router.post("/refresh")
async def refresh_token(payload: RefreshDTO):
    token_pair = await AuthService.refresh_token(payload=payload)
    response = SuccessResponse(http_code=200, status_code=200, message=MessageConsts.SUCCESS, data=token_pair)
    return JSONResponse(status_code=response.http_code, content=response.to_dict())