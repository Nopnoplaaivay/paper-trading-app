from fastapi import Depends
from starlette.responses import JSONResponse

from src.common.consts import MessageConsts
from src.common.responses.base import BaseResponse
from src.common.responses import SuccessResponse
from src.modules.accounts.handlers import accounts_router
from src.modules.accounts.services import AccountsService
from src.modules.auth.decorators import UserPayload
from src.modules.auth.guards import auth_guard
from src.modules.auth.types import JwtPayload
from src.modules.accounts.dtos import DepositDTO, WithdrawDTO


@accounts_router.get("/balance", dependencies=[Depends(auth_guard)])
async def get_balance(payload: JwtPayload = Depends(UserPayload)):
    account_balance = await AccountsService.get_balance(payload=payload)
    if not account_balance:
        response = BaseResponse(
            http_code=404,
            status_code=404,
            message=MessageConsts.NOT_FOUND,
            errors="Account balance not found",
        )
        return JSONResponse(status_code=response.http_code, content=response.to_dict())
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=account_balance,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@accounts_router.post("/deposit", dependencies=[Depends(auth_guard)])
async def deposit(payload: DepositDTO, user: JwtPayload = Depends(UserPayload)):
    account_balance = await AccountsService.deposit(payload=payload, user=user)
    if not account_balance:
        response = BaseResponse(
            http_code=404,
            status_code=404,
            message=MessageConsts.NOT_FOUND,
            errors="Account balance not found",
        )
        return JSONResponse(status_code=response.http_code, content=response.to_dict())
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=account_balance,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@accounts_router.post("/withdraw", dependencies=[Depends(auth_guard)])
async def withdraw(payload: WithdrawDTO, user: JwtPayload = Depends(UserPayload)):
    account_balance = await AccountsService.withdraw(payload=payload, user=user)
    if not account_balance:
        response = BaseResponse(
            http_code=404,
            status_code=404,
            message=MessageConsts.NOT_FOUND,
            errors="Account balance not found",
        )
        return JSONResponse(status_code=response.http_code, content=response.to_dict())
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=account_balance,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())