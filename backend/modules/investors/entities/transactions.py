from sqlalchemy import Column, Integer, String, ForeignKey
from uuid import uuid4

from backend.common.consts import SQLServerConsts
from backend.modules.base.entities import Base



class Transactions(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        {"schema": SQLServerConsts.INVESTORS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.INVESTORS_SCHEMA}].[{__tablename__}]"

    id = Column(String, primary_key=True, index=True, nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String, nullable=False)
    account_id = Column(String, ForeignKey(f"{SQLServerConsts.INVESTORS_SCHEMA}.[accounts].[id]"), nullable=False)