import json
from typing import Dict

from backend.cache import RedisClient
from backend.utils.logger import LOGGER


class SessionCache:
    client = RedisClient

    @classmethod
    def add(cls, session: Dict):
        cache_key = f"session:{session['floorCode']}"
        cls.client.set(cache_key, json.dumps(session))

    @classmethod
    def get_session(cls, floor_code: str) -> Dict:
        cache_key = f"session:{floor_code}"
        session = json.loads(cls.client.get(cache_key)) if cls.client.get(cache_key) else None
        return session

    @classmethod
    def get_all(cls) -> Dict:
        keys = cls.client.keys("session:*")
        sessions = {}
        for key in keys:
            session = json.loads(cls.client.get(key))
            sessions[key] = session
        return sessions