from typing import Dict

from backend.db.sessions import backend_session_scope
from backend.modules.base.query_builder import BaseQueryBuilder
from backend.modules.base.repositories import BaseRepo
from backend.modules.users.entities import Sessions


class SessionsRepo(BaseRepo[Dict]):
    entity = Sessions
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope