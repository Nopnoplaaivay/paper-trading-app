import os
import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

from src.common.consts import MessageConsts
from src.common.responses.exceptions.base_exceptions import BaseExceptionResponse
from src.modules.auth.dtos import RegisterDTO, LoginDTO
from src.modules.auth.types import JwtPayload, RefreshPayload
from src.modules.users.entities import Users, Sessions
from src.modules.users.repositories import UsersRepo, SessionsRepo
from src.utils.jwt_utils import JWTUtils


class AuthService:
    @classmethod
    async def register(cls, payload: RegisterDTO) -> None:
        if await UsersRepo.get_by_condition({Users.account.name: payload.account}):
            raise BaseExceptionResponse(http_code=400, status_code=400, message=MessageConsts.BAD_REQUEST, errors="Account already exists")
        if payload.password != payload.confirm_password:
            raise BaseExceptionResponse(http_code=400, status_code=400, message=MessageConsts.BAD_REQUEST, errors="Passwords do not match")
        await UsersRepo.insert(
            record={
                Users.account.name: payload.account,
                Users.password.name: hashlib.sha256(payload.password.encode('utf-8')).hexdigest(),
                Users.role.name: payload.role,
                Users.type_broker.name: payload.type_broker,
                Users.type_client.name: payload.type_client
            },
            returning=False
        )

    @classmethod
    async def login(cls, payload: LoginDTO) -> Dict[str, str]:
        records = await UsersRepo.get_by_condition({Users.account.name: payload.account})
        user = records[0] if records else None
        if not user:
            raise BaseExceptionResponse(
                http_code=400, status_code=400, message=MessageConsts.BAD_REQUEST, errors="Account does not exist"
            )
        if user[Users.password.name] != hashlib.sha256(payload.password.encode('utf-8')).hexdigest():
            raise BaseExceptionResponse(http_code=401, status_code=401, message=MessageConsts.UNAUTHORIZED, errors="Invalid credentials")
        return await cls.create_token_pair(user)

    @classmethod
    async def create_token_pair(cls, user: Dict) -> Dict[str, str]:
        signature = os.urandom(16).hex()
        expires_at = datetime.now() + timedelta(hours=1)
        session = await SessionsRepo.insert(
            record={
                Sessions.user_id.name: user["id"],
                Sessions.signature.name: signature,
                Sessions.expires_at.name: expires_at
            },
            returning=True
        )

        print(session[Sessions.id.name])
        print(user)

        at_payload = JwtPayload(
            sessionId=session[Sessions.id.name], 
            userId=user[Users.id.name], 
            role=user[Users.role.name]
        )
        rt_payload = RefreshPayload(
            sessionId=session[Sessions.id.name], 
            userId=user[Users.id.name], 
            role=user[Users.role.name],
            signature=signature
        )

        access_token = JWTUtils.create_access_token(payload=at_payload)
        refresh_token = JWTUtils.create_refresh_token(payload=rt_payload)

        return {"accessToken": access_token, "refreshToken": refresh_token}


    # async def logout(self, payload: Dict[str, str]):
    #     session_id = payload["session_id"]
    #     user_id = payload["user_id"]
    #     exp = payload["exp"]
    #     key = f"SESSION_BLACKLIST:{user_id}:{session_id}"
    #     await self._add_to_blacklist(key, exp)
    #     session = await SessionEntity.find_one({"id": session_id})
    #     if session:
    #         await SessionEntity.delete(session)

    # async def refresh_token(self, payload: Dict[str, str]):
    #     session = await SessionEntity.find_one({"id": payload["session_id"]})
    #     if not session or session.signature != payload["signature"]:
    #         sessions = await SessionEntity.find({"user_id": payload["user_id"]})
    #         await SessionEntity.delete_many(sessions)
    #         raise HTTPException(status_code=401, detail="Invalid session")
    #     new_signature = self._create_signature()
    #     access_token = create_access_token(payload)
    #     refresh_token = create_refresh_token({**payload, "signature": new_signature})
    #     await SessionEntity.update(session.id, {"signature": new_signature})
    #     return {"access_token": access_token, "refresh_token": refresh_token}

    # ==================== PRIVATE METHODS ================== #

    # def _create_signature(self) -> str:
    #     return secrets.token_hex(16)

    # async def _add_to_blacklist(self, key: str, exp: int):
    #     ttl = exp * 1000 - int(datetime.utcnow().timestamp() * 1000)
    #     await self.cache_manager.set(key, True, ttl)


    # def get_unique_username(self, given_name: str, family_name: str) -> str:
    #     base_username = (given_name + family_name).normalize("NFD").encode("ascii", "ignore").decode().replace(" ", "")
    #     random_suffix = secrets.token_urlsafe(6)
    #     return f"{base_username}{random_suffix}"