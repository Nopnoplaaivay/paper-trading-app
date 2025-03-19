import hashlib
from datetime import datetime, timedelta
import secrets
from typing import Dict, Optional
from fastapi import HTTPException

from src.common.consts import MessageConsts
from src.common.responses.exceptions.base_exceptions import BaseExceptionResponse
from src.modules.auth.dtos import RegisterDTO, LoginDTO
from src.modules.users.entities import Users
from src.modules.users.repositories import UsersRepo
# from .config.auth_config import AuthConfig
# from .entities.user_entity import UserEntity, SessionEntity
# from .utils.jwt_utils import create_access_token, create_refresh_token

class AuthService:
    # def __init__(self, cache_manager = None):
    #     self.cache_manager = cache_manager

    # ==================== START ROUTE ====================== #
    @classmethod
    async def register(cls, payload: RegisterDTO):
        if await UsersRepo.get_by_condition({Users.account.name: payload.account}):
            raise BaseExceptionResponse(http_code=400, status_code=400, message=MessageConsts.BAD_REQUEST, errors="Account already exists")
        if payload.password != payload.confirm_password:
            raise BaseExceptionResponse(http_code=400, status_code=400, message=MessageConsts.BAD_REQUEST, errors="Passwords do not match")
        hashed_password = await cls._hash_password(payload.password)
        await UsersRepo.insert(
            record={
                Users.account.name: payload.account,
                Users.password.name: hashed_password,
                Users.role.name: payload.role,
                Users.type_broker.name: payload.type_broker,
                Users.type_client.name: payload.type_client
            },
            returning=False
        )

    # async def login(self, dto: LoginDto):
    #     user = await UserEntity.find_one({"email": dto.email})
    #     if not user or not await self._verify_password(user.password, dto.password):
    #         raise HTTPException(status_code=401, detail="Invalid credentials")
    #     return await self.create_token_pair(user)

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
    @staticmethod
    async def _hash_password(plain: str) -> str:
        return hashlib.sha256(plain.encode('utf-8')).hexdigest()

    # async def _verify_password(self, hashed: str, plain: str) -> bool:
    #     try:
    #         return await argon2.verify(hashed, plain)
    #     except Exception:
    #         return False

    # def _create_signature(self) -> str:
    #     return secrets.token_hex(16)

    # async def _add_to_blacklist(self, key: str, exp: int):
    #     ttl = exp * 1000 - int(datetime.utcnow().timestamp() * 1000)
    #     await self.cache_manager.set(key, True, ttl)

    # async def create_token_pair(self, user: UserEntity):
    #     refresh_token_ttl = self.auth_config.AUTH_REFRESH_TOKEN_EXPIRES_IN
    #     signature = self._create_signature()
    #     session = await SessionEntity.save(
    #         SessionEntity(
    #             signature=signature,
    #             user=user,
    #             expires_at=datetime.utcnow() + timedelta(seconds=refresh_token_ttl),
    #         )
    #     )
    #     payload = {
    #         "user_id": user.id,
    #         "session_id": session.id,
    #         "role": user.role,
    #     }
    #     access_token = create_access_token(payload)
    #     refresh_token = create_refresh_token({**payload, "signature": signature})
    #     return {"access_token": access_token, "refresh_token": refresh_token}

    # def get_unique_username(self, given_name: str, family_name: str) -> str:
    #     base_username = (given_name + family_name).normalize("NFD").encode("ascii", "ignore").decode().replace(" ", "")
    #     random_suffix = secrets.token_urlsafe(6)
    #     return f"{base_username}{random_suffix}"