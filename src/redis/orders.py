import json
from typing import Dict

from src.redis import RedisClient
from src.utils.logger import LOGGER


class OrdersCache:
    client = RedisClient

    @classmethod
    async def add(cls, order: Dict):
        cache_key = f"order:{order['symbol']}"
        LOGGER.info(f"Cached order [{order['symbol']}:{order}]")
        cls.client.hset(cache_key, f"{order['id']}", json.dumps(order))  

    @classmethod
    async def get_all(cls, symbol: str) -> Dict:
        cache_key = f"order:{symbol}"
        orders = cls.client.hgetall(cache_key)
        return {k: json.loads(v) for k, v in orders.items()}