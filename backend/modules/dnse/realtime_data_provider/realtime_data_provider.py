from backend.cache.config import DNSEConfigs
from backend.cache.connector import REDIS_POOL
from backend.utils.logger import LOGGER
from backend.common.responses.exceptions import BaseExceptionResponse


class RealtimeDataProvider:
    redis_conn = REDIS_POOL.get_conn()

    @classmethod
    def get_market_price(cls, symbol: str):
        price_key = f"{DNSEConfigs.KEY_OHLC}:{symbol}"
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

    @classmethod
    def get_market_index_info(cls, market_id):
        market_key = f"{DNSEConfigs.KEY_MARKET}:{market_id}"
        market_info = cls.redis_conn.hgetall(market_key)

        if not market_info:
            LOGGER.error(f"Market info not found for market_id: {market_id}")
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message="Market info not found",
                errors="MARKET_INFO_NOT_FOUND",
            )

        index_value = float(market_info.get("valueIndexes", 1500))
        changed = float(market_info.get("changedValue", 0))
        # last_value = float(index_value) + float(changed)
        # pct_changed = (float(changed) / last_value) * 100 if last_value else 0
        pct_changed = float(market_info.get("changedRatio", 0))

        return {
            "market_id": market_id,
            "value": index_value,
            "pct_change": pct_changed,
            "change": changed,
        }

    @classmethod
    def get_stock_data(cls, symbol):
        stock_info_key = f"{DNSEConfigs.KEY_STOCK_INFO}:{symbol}"
        stock_info = cls.redis_conn.hgetall(stock_info_key)

        stock_ohlc_key = f"{DNSEConfigs.KEY_OHLC}:{symbol}"
        stock_ohlc = cls.redis_conn.hgetall(stock_ohlc_key)

        if not stock_info:
            LOGGER.error(f"Stock info not found for symbol: {symbol}")
            raise BaseExceptionResponse(
                http_code=404,
                status_code=404,
                message="Stock info not found",
                errors="STOCK_INFO_NOT_FOUND",
            )

        data = {
            "symbol": symbol,
            "price": float(stock_info.get("matchPrice", 0)),
            "change": float(stock_info.get("changed", 0)),
            "pct_change": float(stock_info.get("changedRatio", 0)),
            "open": float(stock_ohlc.get("open", 0)),
            "high": float(stock_ohlc.get("high", 0)),
            "low": float(stock_ohlc.get("low", 0)),
            "close": float(stock_ohlc.get("close", 0)),
            "volume": float(stock_ohlc.get("volume", 0)),
            "ref": float(stock_info.get("basicPrice", 0)),
            "ceil": float(stock_info.get("ceilingPrice", 0)),
            "floor": float(stock_info.get("floorPrice", 0)),
        }

        return data