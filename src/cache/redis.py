import redis
import json

from typing import Dict


class OrderCache:
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    @classmethod
    async def add_order(cls, order: Dict):
        cache_key = f"pending_orders:{order['symbol']}:{order['side']}"
        cls.client.hset(cache_key, order['id'], json.dumps(order))

    @classmethod
    async def get_orders(cls, symbol: str, side: str):
        cache_key = f"pending_orders:{symbol}:{side}"
        orders = cls.client.hgetall(cache_key)
        return {k: json.loads(v) for k, v in orders.items()}

    @classmethod
    async def remove_order(cls, symbol: str, side: str, order_id: str):
        cache_key = f"pending_orders:{symbol}:{side}"
        cls.client.hdel(cache_key, order_id)