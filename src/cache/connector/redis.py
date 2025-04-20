import os
import redis

from src.utils.logger import LOGGER


class RedisConnectionPool:
    def __init__(self, host, port, db, decode_responses):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses
        )

    def get_conn(self):
        """Lấy một kết nối Redis từ pool."""
        try:
            conn = redis.Redis(connection_pool=self.pool)
            conn.ping()
            return conn
        except redis.ConnectionError as e:
            LOGGER.error(f"Failed to connect to Redis server: {e}")
            return None


REDIS_POOL = RedisConnectionPool(host=os.getenv("REDIS_HOST"), port=6379, db=0, decode_responses=True)