from fastapi import Request
from typing import Optional

from src.common.responses.exceptions import BaseExceptionResponse
from src.common.consts import MessageConsts
from src.modules.auth.services import AuthService
from src.modules.auth.guards.reflector import Reflector


IS_PUBLIC = "isPublic"
IS_REFRESH_TOKEN = "isRefreshToken"


# AuthGuard implementation
class AuthGuard:
    def __call__(self, name = "AuthGuard"):
        # Check if the route is public
        print(f"Calling AuthGuard... {name}")
    #     print(f"AuthGuard is being called with request path: {request.url.path}")

    #     handler = request.state.handler
    #     class_ = request.state.class_
    #     is_public = Reflector.get_all_and_override(IS_PUBLIC, [class_, handler])
    #     if is_public:
    #         return True

    #     is_refresh_token = Reflector.get_all_and_override(IS_REFRESH_TOKEN, [class_, handler])

    #     token = self.extract_token_from_header(request)
    #     if not token:
    #         raise BaseExceptionResponse(
    #             http_code=401,
    #             status_code=401,
    #             message=MessageConsts.UNAUTHORIZED,
    #             errors="Missing or invalid token"
    #         )
    #     if is_refresh_token:
    #         request.state.user = await AuthService.verify_refresh_token(refresh_token=token)
    #     else:
    #         request.state.user = await AuthService.verify_access_token(access_token=token)
    #         print(f"request.state.user: {request.state.user}")
    #     # request.state.user = await AuthService.verify_access_token(access_token=token)
    #     return True

    # def extract_token_from_header(request: Request) -> Optional[str]:
    #     auth_header = request.headers.get("Authorization")
    #     if not auth_header:
    #         return None
        
    #     parts = auth_header.split()
    #     if len(parts) == 2 and parts[0].lower() == "bearer":
    #         return parts[1]
    #     return None
    
auth_guard = AuthGuard()

auth_guard("AuthGuard instance")  # Call the AuthGuard instance with a name argument

