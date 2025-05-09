class DNSEConfigs:
    NUM_REDIS_WORKERS = 2

    KEY_STOCK_INFO = "SI"
    KEY_OHLC = "OHLC"
    KEY_TICK = "TICK"
    KEY_MARKET = "MARKET"

    TOPIC_STOCK_INFO = "plaintext/quotes/krx/mdds/stockinfo/v1/roundlot/symbol"
    TOPIC_OHLC_1M = "plaintext/quotes/krx/mdds/v2/ohlc/stock/1"
    TOPIC_TICK = "plaintext/quotes/krx/mdds/tick/v1/roundlot/symbol"
    TOPIC_MARKET = "plaintext/quotes/krx/mdds/index"
