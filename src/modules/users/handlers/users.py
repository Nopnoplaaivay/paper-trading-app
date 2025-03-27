from fastapi import Depends
from starlette.responses import JSONResponse

from src.common.consts import MessageConsts
from src.common.responses.base import BaseResponse
from src.common.responses import SuccessResponse
from src.modules.users.handlers import user_router
from src.modules.users.services import AccountsService
from src.modules.auth.decorators import Payload
from src.modules.auth.guards import AuthGuard, auth_guard
from src.modules.auth.types import JwtPayload

@user_router.get("/balance", dependencies=[Depends(auth_guard)])
async def get_balance(payload: JwtPayload = Depends(Payload)):
    account_balance = await AccountsService.get_balance(user_id=payload.userId)
    if not account_balance:
        response = BaseResponse(http_code=404, status_code=404, message=MessageConsts.NOT_FOUND, errors="Account balance not found")
        return JSONResponse(status_code=response.http_code, content=response.to_dict())
    response = SuccessResponse(http_code=200, status_code=200, message=MessageConsts.SUCCESS, data=account_balance)
    return JSONResponse(status_code=response.http_code, content=response.to_dict())