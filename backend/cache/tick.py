import json
from typing import Dict

from backend.cache import RedisClient
from backend.utils.logger import LOGGER


class TickCache:
    client = RedisClient

    @classmethod
    def add(cls, tick: Dict):
        cache_key = f"match_price:{tick['symbol']}"
        match_price = int(tick['matchPrice'] * 1000)
        cls.client.set(cache_key, match_price, ex=10*60*60)  # 9 hours

    @classmethod
    def get_match_price(cls, symbol: str) -> Dict:
        cache_key = f"match_price:{symbol}"
        tick = cls.client.get(cache_key)
        match_price = json.loads(tick) if tick else -1
        return match_price
