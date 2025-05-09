from typing import Dict

from backend.db.sessions import backend_session_scope
from backend.modules.base.query_builder import BaseQueryBuilder
from backend.modules.base.repositories import BaseRepo
from backend.modules.market_data.entities import StockInfo


class StockInfoRepo(BaseRepo[Dict]):
    entity = StockInfo
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope
