import os
import hashlib
import uuid
import jwt
from cachetools import TTLCache
from datetime import datetime, timedelta
from typing import Dict, Optional

from src.common.consts import MessageConsts, CommonConsts
from src.common.responses.exceptions.base_exceptions import BaseExceptionResponse
from src.modules.auth.dtos import RegisterDTO, LoginDTO
from src.modules.auth.types import JwtPayload, RefreshPayload
from src.modules.users.entities import Users, Sessions
from src.modules.users.repositories import UsersRepo, SessionsRepo
from src.utils.jwt_utils import JWTUtils
from src.utils.logger import LOGGER


black_list = TTLCache(maxsize=1000, ttl=24 * 60 * 60)


class AuthService:
    @classmethod
    async def register(cls, payload: RegisterDTO) -> None:
        if await UsersRepo.get_by_condition({Users.account.name: payload.account}):
            raise BaseExceptionResponse(
                http_code=400,
                status_code=400,
                message=MessageConsts.BAD_REQUEST,
                errors="Account already exists",
            )
        if payload.password != payload.confirm_password:
            raise BaseExceptionResponse(
                http_code=400,
                status_code=400,
                message=MessageConsts.BAD_REQUEST,
                errors="Passwords do not match",
            )
        salted_password = f"{CommonConsts.SALT}{payload.password}"
        await UsersRepo.insert(
            record={
                Users.account.name: payload.account,
                Users.password.name: hashlib.sha256(
                    salted_password.encode("utf-8")
                ).hexdigest(),
                Users.role.name: payload.role,
                Users.type_broker.name: payload.type_broker,
                Users.type_client.name: payload.type_client,
            },
            returning=False,
        )
        LOGGER.info(f"User {payload.account} has been created")

    @classmethod
    async def login(cls, payload: LoginDTO) -> Dict[str, str]:
        records = await UsersRepo.get_by_condition(
            {Users.account.name: payload.account}
        )
        user = records[0] if records else None
        if not user:
            raise BaseExceptionResponse(
                http_code=400,
                status_code=400,
                message=MessageConsts.BAD_REQUEST,
                errors="Account does not exist",
            )
        salted_password = f"{CommonConsts.SALT}{payload.password}"
        if (
            user[Users.password.name]
            != hashlib.sha256(salted_password.encode("utf-8")).hexdigest()
        ):
            raise BaseExceptionResponse(
                http_code=401,
                status_code=401,
                message=MessageConsts.UNAUTHORIZED,
                errors="Invalid credentials",
            )
        return await cls.create_token_pair(user)

    @classmethod
    async def create_token_pair(cls, user: Dict) -> Dict[str, str]:
        session_id = str(uuid.uuid4())
        signature = os.urandom(16).hex()
        expires_at = datetime.now() + timedelta(hours=1)
        session = await SessionsRepo.insert(
            record={
                Sessions.id.name: session_id,
                Sessions.user_id.name: user["id"],
                Sessions.signature.name: signature,
                Sessions.expires_at.name: expires_at,
            },
            returning=True,
        )

        at_payload = JwtPayload(
            sessionId=session[Sessions.id.name],
            userId=user[Users.id.name],
            role=user[Users.role.name],
        )
        rt_payload = RefreshPayload(
            sessionId=session[Sessions.id.name],
            userId=user[Users.id.name],
            role=user[Users.role.name],
            signature=signature,
        )

        access_token = JWTUtils.create_access_token(payload=at_payload)
        refresh_token = JWTUtils.create_refresh_token(payload=rt_payload)

        return {"accessToken": access_token, "refreshToken": refresh_token}

    @classmethod
    async def logout(self, payload: JwtPayload):
        key = f"SESSION_BLACKLIST:{payload.userId}:{payload.sessionId}"
        black_list[key] = payload.exp
        session = await SessionsRepo.get_by_condition(
            {Sessions.id.name: payload.sessionId}
        )
        if session:
            await SessionsRepo.delete({Sessions.id.name: payload.sessionId})

        # show black list
        LOGGER.info(f"Black list: {black_list}")
        LOGGER.info(f"User {payload.userId} has been logged out")

    @classmethod
    async def refresh_token(cls, payload: RefreshPayload):
        sessions = await SessionsRepo.get_by_condition(
            {Sessions.id.name: payload.sessionId}
        )
        if len(sessions) == 0:
            raise BaseExceptionResponse(
                http_code=401,
                status_code=401,
                message=MessageConsts.UNAUTHORIZED,
                errors="Invalid session",
            )
        session = sessions[0]
        if session[Sessions.signature.name] != payload.signature:
            # Remove all sessions of the user
            await SessionsRepo.delete(
                {Sessions.user_id.name: payload.userId}
            )
            raise BaseExceptionResponse(
                http_code=401,
                status_code=401,
                message=MessageConsts.UNAUTHORIZED,
                errors="Invalid signature"
            )
        
        new_signature = os.urandom(16).hex()
        await SessionsRepo.update(
            record={
                Sessions.id.name: payload.sessionId,
                Sessions.signature.name: new_signature,
            },
            identity_columns=[Sessions.id.name],
            returning=False,
        )

        access_token_payload = JwtPayload(
            sessionId=session[Sessions.id.name],
            userId=payload.userId,
            role=payload.role,
        )
        refresh_token_payload = RefreshPayload(
            sessionId=session[Sessions.id.name],
            userId=payload.userId,
            role=payload.role,
            signature=new_signature,
        )

        access_token = JWTUtils.create_access_token(payload=access_token_payload)
        refresh_token = JWTUtils.create_refresh_token(payload=refresh_token_payload)
        return {"accessToken": access_token, "refreshToken": refresh_token}
