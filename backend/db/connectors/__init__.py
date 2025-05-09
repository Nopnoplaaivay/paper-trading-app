from .sql_server import AsyncSQLServerConnectorPool
import contextvars

CONTEXTVAR = contextvars.ContextVar("var", default=None)
