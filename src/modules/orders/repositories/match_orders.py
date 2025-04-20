from typing import Dict

from src.db.sessions import backend_session_scope
from src.modules.base.query_builder import BaseQueryBuilder
from src.modules.base.repositories import BaseRepo
from src.modules.orders.entities import MatchOrders


class MatchOrdersRepo(BaseRepo[Dict]):
    entity = MatchOrders
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope