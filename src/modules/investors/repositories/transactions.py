from typing import Dict

from src.db.sessions import backend_session_scope
from src.modules.base.query_builder import BaseQueryBuilder
from src.modules.base.repositories import BaseRepo
from src.modules.investors.entities import Transactions


class TransactionsRepo(BaseRepo[Dict]):
    entity = Transactions
    query_builder = BaseQueryBuilder(entity=entity)
    session_scope = backend_session_scope