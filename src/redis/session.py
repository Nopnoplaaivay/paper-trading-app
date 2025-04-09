import json
from typing import Dict

from src.redis import RedisClient
from src.utils.logger import LOGGER


class SessionCache:
    client = RedisClient

    @classmethod
    async def add(cls, session: Dict):
        cache_key = f"session:{session['floorCode']}"
        cls.client.set(cache_key, json.dumps(session))

    @classmethod
    async def get_session(cls, floor_code: str) -> Dict:
        cache_key = f"session:{floor_code}"
        session = json.loads(cls.client.get(cache_key)) if cls.client.get(cache_key) else None
        return session