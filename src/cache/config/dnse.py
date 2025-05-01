class DNSEConfigs:
    NUM_REDIS_WORKERS = 2

    KEY_STOCK_INFO = "SI"
    KEY_OHLC = "OHLC"
    KEY_SESSION = "SESSION"
    KEY_TICK = "TICK"
    KEY_MARKET = "MARKET"

    TOPIC_STOCK_INFO = "plaintext/quotes/stock/SI"
    TOPIC_SESSION = "plaintext/quotes/session"
    TOPIC_OHLC_1M = "plaintext/quotes/stock/OHLC/1"
    TOPIC_TICK = "plaintext/quotes/stock/tick"
    TOPIC_MARKET = "plaintext/quotes/index/MI"