from datetime import datetime, timedelta
from jose import jwt

def create_access_token(payload: dict, secret: str, expires_in: int) -> str:
    expire = datetime.utcnow() + timedelta(seconds=expires_in)
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm="HS256")

def create_refresh_token(payload: dict, secret: str, expires_in: int) -> str:
    expire = datetime.utcnow() + timedelta(seconds=expires_in)
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm="HS256")