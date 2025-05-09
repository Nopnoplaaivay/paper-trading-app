from fastapi import Depends
from starlette.responses import JSONResponse

from backend.common.consts import MessageConsts
from backend.common.responses.base import BaseResponse
from backend.common.responses import SuccessResponse
from backend.modules.admin.handlers import admin_router
from backend.modules.admin.services import AdminService
from backend.modules.auth.decorators import UserPayload
from backend.modules.auth.guards import auth_guard, admin_guard
from backend.modules.auth.types import JwtPayload
from backend.modules.admin.dtos import UpdateUserRoleDTO, AdminCancelOrdersDTO


@admin_router.get("/user_management", dependencies=[Depends(auth_guard), Depends(admin_guard)])
async def get_users(user: JwtPayload = Depends(UserPayload)):
    users = await AdminService.get_all_users()
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=users,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@admin_router.post("/user_management/update", dependencies=[Depends(auth_guard), Depends(admin_guard)])
async def update_user_role(payload: UpdateUserRoleDTO, user: JwtPayload = Depends(UserPayload)):
    updated_user = await AdminService.update_user(payload=payload)
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=updated_user,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@admin_router.post("/orders_management", dependencies=[Depends(auth_guard), Depends(admin_guard)])
async def get_orders(user: JwtPayload = Depends(UserPayload)):
    orders = await AdminService.get_all_orders()
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=orders,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@admin_router.put("/orders_management/cancel", dependencies=[Depends(auth_guard), Depends(admin_guard)])
async def cancel_order(payload: AdminCancelOrdersDTO, user: JwtPayload = Depends(UserPayload)):
    order = await AdminService.cancel_order(payload=payload)
    if not order:
        response = BaseResponse(
            http_code=404,
            status_code=404,
            message=MessageConsts.NOT_FOUND,
            errors="Order is not found or pending",
        )
        return JSONResponse(status_code=response.http_code, content=response.to_dict())
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=order,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())
