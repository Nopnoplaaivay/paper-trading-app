from fastapi import Request

from src.common.responses.exceptions import BaseExceptionResponse

ROLE_KEY = "role_key"


class RoleGuard:
    async def activate(request: Request, required_role: str = None):
        if not required_role:
            return True 

        user = getattr(request.state, "user", None)
        if not user:
            raise BaseExceptionResponse(
                http_code=401,
                status_code=401,
                message="Unauthorized",
                errors="Missing or invalid token"
            )
        return True
    
async def role_guard(request: Request):
    return await RoleGuard.activate(request)