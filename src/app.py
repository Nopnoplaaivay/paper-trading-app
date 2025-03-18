import json
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import crawl_api_router, token_api_router
from src.common.consts import MessageConsts, CommonConsts
from src.common.responses.exceptions import BaseExceptionResponse
from src.utils.logger import LOGGER


crawl_app = FastAPI(
    title="CRAWL APP FIINX",
    description="Welcome to API documentation",
    # root_path="/api/v1",
    docs_url="/docs" if CommonConsts.DEBUG else None,
    # openapi_url="/docs/openapi.json",
    redoc_url="/docs" if CommonConsts.DEBUG else None,
)
crawl_cors = CORSMiddleware(
    crawl_app, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

token_app = FastAPI(
    title="CRAWL APP FIINX",
    description="Welcome to API documentation",
    # root_path="/api/v1",
    docs_url="/docs" if CommonConsts.DEBUG else None,
    # openapi_url="/docs/openapi.json",
    redoc_url="/docs" if CommonConsts.DEBUG else None,
)
token_cors = CORSMiddleware(
    token_app, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


async def pydantic_exception_handler(request: Request, exception: RequestValidationError):
    errors = {}
    for error in exception.errors():
        field = []
        _errors = errors
        if len(error["loc"]) == 1:
            if "ctx" in error and "discriminator_key" in error["ctx"]:
                field = error["ctx"]["discriminator_key"]
                if field not in _errors:
                    _errors[field] = []
                _errors[field].append(error["msg"])
                continue
        for i in range(1, len(error["loc"])):
            field = error["loc"][i]
            if field not in _errors:
                _errors[field] = [] if i == len(error["loc"]) - 1 else {}
            _errors = _errors[field]
        _errors.append(error["msg"])
    exception = BaseExceptionResponse(
        http_code=400,
        status_code=400,
        message=MessageConsts.BAD_REQUEST,
        errors=errors,
    )
    error_response = exception.to_dict()
    LOGGER.error(json.dumps(error_response))
    return JSONResponse(
        status_code=exception.http_code,
        content=error_response,
    )


async def response_exception_handler(request: Request, exception):
    if isinstance(exception, BaseExceptionResponse):
        error_response = exception.to_dict()
    else:
        errors = (
            None if not CommonConsts.DEBUG else {"key": MessageConsts.INTERNAL_SERVER_ERROR, "message": str(exception)}
        )
        exception = BaseExceptionResponse(
            http_code=500,
            status_code=500,
            message=MessageConsts.INTERNAL_SERVER_ERROR,
            errors=errors,
        )
        error_response = exception.to_dict()
    LOGGER.error(json.dumps(error_response))
    return JSONResponse(
        status_code=exception.http_code,
        content=error_response,
    )


@crawl_app.exception_handler(RequestValidationError)
async def exception_handler(request, exception):
    return await pydantic_exception_handler(request=request, exception=exception)


@crawl_app.exception_handler(Exception)
async def exception_handler(request, exception):
    return await response_exception_handler(request=request, exception=exception)


@token_app.exception_handler(RequestValidationError)
async def exception_handler(request, exception):
    return await pydantic_exception_handler(request=request, exception=exception)


@token_app.exception_handler(Exception)
async def exception_handler(request, exception):
    return await response_exception_handler(request=request, exception=exception)


crawl_app.include_router(prefix="/api/v1", router=crawl_api_router)
token_app.include_router(prefix="/api/v1", router=token_api_router)
