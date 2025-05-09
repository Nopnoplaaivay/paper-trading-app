import json
from typing import Dict, List

from backend.cache import RedisClient


class StockCache:
    client = RedisClient

    @classmethod
    def add(cls, stock_info: Dict):
        cache_key = f"stock_info:{stock_info['symbol']}"
        cls.client.set(cache_key, json.dumps(stock_info))

    @classmethod
    def get_all(cls) -> List[Dict]:
        keys = cls.client.keys("stock_info:*")
        stock_infos = []
        for key in keys:
            ohlc = cls.client.get(key)
            if ohlc:
                stock_infos.append(json.loads(ohlc))
        return stock_infos