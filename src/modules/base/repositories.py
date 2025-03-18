from typing import List, TypeVar, Generic, Dict, Union, Callable

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from src.modules.base.entities import Base
from src.modules.base.query_builder import BaseQueryBuilder, TextSQL

T = TypeVar("T", bound=Base)


class BaseRepo(Generic[T]):
    entity: T
    query_builder: BaseQueryBuilder
    session_scope: Callable[..., Session]

    @classmethod
    async def data_frame_factory(cls, cur) -> pd.DataFrame:
        if cur.description is None:
            return pd.DataFrame()
        columns = [column[0] for column in cur.description]
        results = [list(row) for row in cur.fetchall()]
        return pd.DataFrame(results, columns=columns, dtype=np.dtype("O"))

    @classmethod
    async def row_factory(cls, cur) -> List[Dict]:
        if cur.description is None:
            return []
        columns = [column[0] for column in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    @classmethod
    async def insert_many(cls, records: List[Dict], returning):
        with cls.session_scope() as session:
            insert_query = cls.query_builder.insert_many(records=records, returning=returning)
            cur = session.connection().exec_driver_sql(insert_query.sql, tuple(insert_query.params)).cursor
            if returning:
                return await cls.row_factory(cur=cur)
            else:
                return None

    @classmethod
    async def insert(cls, record: Dict, returning) -> Dict:
        results = await cls.insert_many(records=[record], returning=returning)
        if returning:
            return results[0]
        else:
            return None

    @classmethod
    async def update_many(
        cls, records: List[Dict], identity_columns: List[str], returning, text_clauses: Dict[str, TextSQL] = None
    ):
        if len(identity_columns) == 0:
            raise Exception("missing require identity columns")
        with cls.session_scope() as session:
            query_values = cls.query_builder.generate_values(records=records, text_clauses=text_clauses)
            update_columns = query_values.columns.copy()
            for col in identity_columns:
                update_columns.remove(col)
            sql_set_columns = ", ".join([f"t.[{col}] = s.[{col}]" for col in update_columns])
            sql_select_columns = ", ".join(f"[{col}]" for col in query_values.columns)
            sql_conditions = " AND ".join([f"t.[{col}] = s.[{col}]" for col in identity_columns])
            sql_returning = "OUTPUT INSERTED.*" if returning else ""
            sql = f"""
                UPDATE t
                SET {sql_set_columns}
                {sql_returning}
                FROM (
                    SELECT *
                    from (
                        {query_values.sql}
                    ) _ ({sql_select_columns})
                ) s
                inner join {cls.query_builder.full_table_name} t on {sql_conditions}
            """
            cur = session.connection().exec_driver_sql(sql, tuple(query_values.params)).cursor
            if returning:
                results = await cls.row_factory(cur=cur)
            else:
                results = None
        return results

    @classmethod
    async def update(
        cls, record: Dict, identity_columns: List[str], returning, text_clauses: Dict[str, TextSQL] = None
    ) -> T:
        results = await cls.update_many(
            records=[record], identity_columns=identity_columns, returning=returning, text_clauses=text_clauses
        )
        if returning:
            return results[0]
        else:
            return None

    @classmethod
    async def get_all(cls) -> List[Dict]:
        with cls.session_scope() as session:
            sql = (
                """
                SELECT *
                FROM %s
            """
                % cls.query_builder.full_table_name
            )
            cur = session.connection().exec_driver_sql(sql).cursor
            results = await cls.row_factory(cur=cur)
        return results


    @classmethod
    async def get_by_id(cls, _id: int):
        return await cls.get_by_condition({cls.entity.id.name: _id})

    @classmethod
    async def get_by_condition(cls, conditions: Dict):
        condition_query = cls.query_builder.where(conditions)
        sql = """
            SELECT *
            FROM
            %s
            WHERE %s
        """ % (
            cls.query_builder.full_table_name,
            condition_query.sql,
        )
        with cls.session_scope() as session:
            cur = session.connection().exec_driver_sql(sql, tuple(condition_query.params)).cursor
            records = await cls.row_factory(cur=cur)
            return records