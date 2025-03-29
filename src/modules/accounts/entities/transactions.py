from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from uuid import uuid4

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base



class Transactions(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        {"schema": SQLServerConsts.ACCOUNTS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.ACCOUNTS_SCHEMA}].[{__tablename__}]"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid4()), index=True, nullable=False)
    account_id = Column(UNIQUEIDENTIFIER, ForeignKey(f"{SQLServerConsts.ACCOUNTS_SCHEMA}.accounts.id"), nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)