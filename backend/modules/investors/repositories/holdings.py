from typing import Dict

from backend.db.sessions import backend_session_scope
from backend.modules.base.query_builder import BaseQueryBuilder
from backend.modules.base.repositories import BaseRepo
from backend.modules.investors.entities import Holdings


class HoldingsRepo(BaseRepo[Dict]):
    entity = Holdings
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope