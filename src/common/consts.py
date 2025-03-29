import os

class SQLServerConsts:
    ASYNC_DNS = os.getenv("ASYNC_DNS")

    AUTH_SCHEMA = "KVS_AUTH"
    ACCOUNTS_SCHEMA = "KVS_ACCOUNTS"
    ORDERS_SCHEMA = "KVS_ORDERS"


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
    INTERNAL_SERVER_ERROR = "Unknown internal server error"
