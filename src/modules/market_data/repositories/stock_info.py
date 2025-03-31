from typing import Dict

from src.db.sessions import backend_session_scope
from src.modules.base.query_builder import BaseQueryBuilder
from src.modules.base.repositories import BaseRepo
from src.modules.market_data.entities import StockInfo


class StockInfoRepo(BaseRepo[Dict]):
    entity = StockInfo
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope
