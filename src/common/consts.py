import os
import random

class SQLServerConsts:
    ASYNC_DNS = os.getenv("ASYNC_DNS")

    AUTH_SCHEMA = "Auth"
    INVESTORS_SCHEMA = "Investors"
    ORDERS_SCHEMA = "Orders"
    MARKET_DATA_SCHEMA = "Market_data"

    TRADING_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    GMT_7_NOW = f"SWITCHOFFSET(SYSUTCDATETIME(), '+07:00')"
    GMT_7_NOW_VARCHAR = f"FORMAT(SWITCHOFFSET(SYSUTCDATETIME(), '+07:00'), 'yyyy-MM-dd HH:mm:ss')"

class CommonConsts:
    ROOT_FOLDER = os.path.abspath(os.path.join(os.path.abspath(__file__), 3 * "../"))

    SALT = os.getenv("SALT")
    AT_SECRET_KEY = os.getenv("AT_SECRET_KEY")
    RT_SECRET_KEY = os.getenv("RT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRES_IN = 3600
    REFRESH_TOKEN_EXPIRES_IN = 86400

    DEBUG = os.getenv("DEBUG") 


class MessageConsts:
    CREATED = "Created"
    SUCCESS = "Success"
    VALIDATION_FAILED = "Validation failed"
    UNAUTHORIZED = "Unauthorized"
    BAD_REQUEST = "Bad request"
    FORBIDDEN = "Forbidden"
    NOT_FOUND = "Not found"
    CONFLICT = "Conflict"
    INVALID_OBJECT_ID = "Invalid object id"
    INVALID_INPUT = "Invalid input"
    INTERNAL_SERVER_ERROR = "Unknown internal server error"

class DNSEConsts:
    BROKER = 'datafeed-lts.dnse.com.vn'
    PORT = 443
    CLIENT_ID = f'python-json-mqtt-ws-sub-{random.randint(0, 1000)}'
    FIRST_RECONNECT_DELAY = 1
    RECONNECT_RATE = 2
    MAX_RECONNECT_COUNT = 12
    MAX_RECONNECT_DELAY = 60

class YfinanceConsts:
    VALID_RANGES = [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max",
    ]

    AVAILABLE_RANGES = [
        "1Y",
        "5Y",
        "10Y"
    ]