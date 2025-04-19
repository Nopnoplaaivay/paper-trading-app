from src.cache import OHLCCache, StockCache


from src.utils.logger import LOGGER


class TradeData:
    @classmethod
    def get_ohlc(cls):
        ohlc = OHLCCache.get_all()
        if not ohlc:
            LOGGER.error(f"Failed to get OHLCCache data")
            return None
        return ohlc

    @classmethod
    def get_stock_info(cls):
        stock_infos = StockCache.get_all()
        if not stock_infos:
            LOGGER.error(f"Failed to get StockCache data")
            return None
        return stock_infos

