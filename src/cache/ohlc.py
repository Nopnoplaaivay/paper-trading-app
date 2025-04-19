import json
from typing import Dict, List

from src.cache import RedisClient
from src.utils.logger import LOGGER


class OHLCCache:
    client = RedisClient

    @classmethod
    def add(cls, ohlc: Dict):
        cache_key = f"ohlc:{ohlc['symbol']}"
        cls.client.set(cache_key, json.dumps(ohlc))

    @classmethod
    def get_close_price(cls, symbol: str) -> Dict:
        cache_key = f"close:{symbol}"
        tick = cls.client.get(cache_key)
        match_price = json.loads(tick) if tick else -1
        return match_price

    @classmethod
    def get_all(cls) -> List[Dict]:
        keys = cls.client.keys("ohlc:*")
        ohlcs = []
        for key in keys:
            ohlc = cls.client.get(key)
            if ohlc:
                ohlcs.append(json.loads(ohlc))
        return ohlcs