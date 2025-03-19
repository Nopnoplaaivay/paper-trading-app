import jwt
import datetime

from src.common.consts import CommonConsts
from src.modules.auth.types import JwtPayload, RefreshPayload
from src.utils.time_utils import TimeUtils


class JWTUtils:
    @staticmethod
    def create_access_token(payload: JwtPayload) -> str:
        expire = TimeUtils.get_current_vn_time() + datetime.timedelta(seconds=CommonConsts.ACCESS_TOKEN_EXPIRES_IN)
        payload_dict = payload.dict()
        payload_dict.update({"exp": expire})
        return jwt.encode(payload_dict, CommonConsts.AT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_token(payload: RefreshPayload) -> str:
        expire = TimeUtils.get_current_vn_time() + datetime.timedelta(seconds=CommonConsts.REFRESH_TOKEN_EXPIRES_IN)
        payload_dict = payload.dict()
        payload_dict.update({"exp": expire})
        return jwt.encode(payload_dict, CommonConsts.RT_SECRET_KEY, algorithm="HS256")