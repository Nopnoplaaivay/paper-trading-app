import jwt
import datetime

from backend.common.consts import CommonConsts
from backend.modules.auth.types import JwtPayload, RefreshPayload
from backend.utils.time_utils import TimeUtils


class JWTUtils:
    @staticmethod
    def create_access_token(payload: JwtPayload) -> str:
        utc_current_time = TimeUtils.get_utc_current_time()
        expire = utc_current_time + datetime.timedelta(seconds=CommonConsts.ACCESS_TOKEN_EXPIRES_IN)
        payload_dict = payload.dict()
        payload_dict.update({"exp": int(expire.timestamp()), "iat": int(utc_current_time.timestamp())})
        return jwt.encode(payload_dict, CommonConsts.AT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_token(payload: RefreshPayload) -> str:
        utc_current_time = TimeUtils.get_utc_current_time()
        expire = utc_current_time + datetime.timedelta(seconds=CommonConsts.REFRESH_TOKEN_EXPIRES_IN)
        payload_dict = payload.dict()
        payload_dict.update({"exp": int(expire.timestamp()), "iat": int(utc_current_time.timestamp())})
        return jwt.encode(payload_dict, CommonConsts.RT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def decode_token(token: str, secret_key: str) -> dict:
        return jwt.decode(token, secret_key, algorithms=["HS256"])
        