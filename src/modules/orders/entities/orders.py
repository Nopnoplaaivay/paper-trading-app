from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from uuid import uuid4

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base



class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        {"schema": SQLServerConsts.ORDERS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.ORDERS_SCHEMA}].[{__tablename__}]"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid4()), index=True, nullable=False)
    account_id = Column(UNIQUEIDENTIFIER, ForeignKey(f"{SQLServerConsts.ACCOUNTS_SCHEMA}.accounts.id"), nullable=False)
    side = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    order_quantity = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False)
    order_status = Column(String, nullable=False)
    filled_quantity = Column(Integer, nullable=False)
    last_quantity = Column(Integer, nullable=False)
    error = Column(String)
    created_at = Column(DateTime, nullable=False)