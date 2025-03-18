from typing import List

from fastapi import APIRouter
from starlette.responses import JSONResponse

from src.common.consts import MessageConsts
from src.modules.base.dto import BaseDTO
from src.modules.common.handlers import get_token_router
from src.modules.crawl.handlers import crawl_router


class ErrorDetailModel(BaseDTO):
    field: List[str]


class ErrorResponseModel(BaseDTO):
    statusCode: int
    message: str
    error: ErrorDetailModel


crawl_api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponseModel},
        401: {"model": ErrorResponseModel},
        422: {"model": ErrorResponseModel},
        500: {"model": ErrorResponseModel},
    },
)

token_api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponseModel},
        401: {"model": ErrorResponseModel},
        422: {"model": ErrorResponseModel},
        500: {"model": ErrorResponseModel},
    },
)

token_api_router.include_router(get_token_router, prefix="/processTracking", tags=["processTracking"])
crawl_api_router.include_router(crawl_router, prefix="/crawl", tags=["crawl"])


@crawl_api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return JSONResponse(status_code=200, content={"message": MessageConsts.SUCCESS})


@token_api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return JSONResponse(status_code=200, content={"message": MessageConsts.SUCCESS})
