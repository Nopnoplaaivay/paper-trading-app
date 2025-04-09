import json
from typing import Dict

from src.redis import RedisClient
from src.utils.logger import LOGGER


class TickCache:
    client = RedisClient

    @classmethod
    async def add(cls, tick: Dict):
        cache_key = f"match_price:{tick['symbol']}"
        match_price = int(tick['matchPrice'] * 1000)
        await cls.client.set(cache_key, match_price, ex=10*60*60)  # 9 hours

    @classmethod
    async def get_match_price(cls, symbol: str) -> Dict:
        cache_key = f"match_price:{symbol}"
        tick = cls.client.get(cache_key)
        match_price = json.loads(tick) if tick else -1
        return match_price