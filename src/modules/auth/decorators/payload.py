from fastapi import Request

from src.modules.auth.types.auth import JwtPayload
from src.common.responses.exceptions import BaseExceptionResponse


def UserPayload(request: Request) -> JwtPayload:
    user = getattr(request.state, "user", None)
    if not user:
        raise BaseExceptionResponse(
            http_code=401,
            status_code=401,
            message="Unauthorized",
            errors="User not authenticated"
        )
    return user