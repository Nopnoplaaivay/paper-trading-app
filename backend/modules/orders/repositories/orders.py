from typing import Dict

from backend.db.sessions import backend_session_scope
from backend.modules.base.query_builder import BaseQueryBuilder
from backend.modules.base.repositories import BaseRepo
from backend.modules.orders.entities import Orders


class OrdersRepo(BaseRepo[Dict]):
    entity = Orders
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope