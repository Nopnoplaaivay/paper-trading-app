from typing import Dict

from backend.db.sessions import backend_session_scope
from backend.modules.base.query_builder import BaseQueryBuilder
from backend.modules.base.repositories import BaseRepo
from backend.modules.market_data.entities import Tick


class TickRepo(BaseRepo[Dict]):
    entity = Tick
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope
