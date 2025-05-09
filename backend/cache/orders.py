import json
from typing import Dict, Optional

from backend.cache import RedisClient
from backend.utils.logger import LOGGER


class OrdersCache:
    client = RedisClient

    @classmethod
    def add(cls, order: Dict):
        cache_key = f"order:{order['symbol']}"
        LOGGER.info(f"Cached order [{order['symbol']}:{order}]")
        cls.client.hset(cache_key, f"{order['id']}", json.dumps(order))  

    @classmethod
    def get_pending_orders(cls, symbol: str) -> Optional[Dict]:
        cache_key = f"order:{symbol}"
        orders = cls.client.hgetall(cache_key)
        return {k: json.loads(v) for k, v in orders.items()} if orders else None
    
    @classmethod
    def remove(cls, symbol: str, order_id: str):
        cache_key = f"order:{symbol}"
        LOGGER.info(f"Removed order [{order_id}]")
        cls.client.hdel(cache_key, order_id)