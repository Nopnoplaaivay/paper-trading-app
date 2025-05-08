from fastapi import Depends
from starlette.responses import JSONResponse

from src.common.consts import MessageConsts
from src.common.responses.base import BaseResponse
from src.common.responses import SuccessResponse
from src.modules.orders.handlers import orders_router
from src.modules.orders.services import OrdersService
from src.modules.orders.dtos import OrdersDTO, PowerDTO, OrdersCancelDTO
from src.modules.auth.decorators import UserPayload
from src.modules.auth.guards import auth_guard
from src.modules.auth.types import JwtPayload


@orders_router.post("/power", dependencies=[Depends(auth_guard)])
async def get_power(payload: PowerDTO):
    power = await OrdersService.get_power(payload=payload)
    if not power:
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
        data=power,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@orders_router.get("/orders", dependencies=[Depends(auth_guard)])
async def get_orders(user: JwtPayload = Depends(UserPayload)):
    orders = await OrdersService.get_orders(payload=user)
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=orders,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@orders_router.post("/orders", dependencies=[Depends(auth_guard)])
async def place_order(payload: OrdersDTO, user: JwtPayload = Depends(UserPayload)):
    order = await OrdersService.place_order(payload=payload, user=user)
    if not order:
        response = BaseResponse(
            http_code=404,
            status_code=404,
            message=MessageConsts.NOT_FOUND,
            errors="Order not found",
        )
        return JSONResponse(status_code=response.http_code, content=response.to_dict())
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS,
        data=order,
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())

@orders_router.delete("/orders", dependencies=[Depends(auth_guard)])
async def cancel_order(payload: OrdersCancelDTO, user: JwtPayload = Depends(UserPayload)):
    await OrdersService.cancel_order(payload=payload, user=user)
    response = SuccessResponse(
        http_code=200,
        status_code=200,
        message=MessageConsts.SUCCESS
    )
    return JSONResponse(status_code=response.http_code, content=response.to_dict())