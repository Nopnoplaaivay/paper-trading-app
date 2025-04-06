import json
from typing import Dict

from src.redis import RedisClient
from src.utils.logger import LOGGER


class OHLCCache:
    client = RedisClient

    @classmethod
    async def add(cls, ohlc: Dict):
        cache_key = f"close:{ohlc['symbol']}"
        close_price = int(ohlc['close'] * 1000)
        # LOGGER.info(f"Cached [{tick['symbol']}: {match_price}]")
        await cls.client.set(cache_key, close_price)  

    @classmethod
    async def get_close_price(cls, symbol: str) -> Dict:
        cache_key = f"close:{symbol}"
        tick = cls.client.get(cache_key)
        match_price = json.loads(tick) if tick else -1
        return match_price