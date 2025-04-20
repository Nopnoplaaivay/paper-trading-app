from src.cache.connector import REDIS_POOL
from src.utils.logger import LOGGER
from src.common.responses.exceptions import BaseExceptionResponse


class RealtimeDataProvider:
    redis_conn = REDIS_POOL.get_conn()

    @classmethod
    def get_market_price(cls, symbol: str):
        price_key = f"OHLC:{symbol}"
        price = int(float(cls.redis_conn.hget(price_key, "close")) * 1000)

        if not price:
            LOGGER.error(f"Price not found for symbol: {symbol}")
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message="Price not found",
                errors="PRICE_NOT_FOUND",
            )

        return price