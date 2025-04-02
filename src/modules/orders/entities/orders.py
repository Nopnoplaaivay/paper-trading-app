from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from enum import Enum
from uuid import uuid4

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base

class OrderStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETE"
    CANCELLED = "FAIL"

class OrderSide(Enum):
    BUY = "SIDE_BUY"
    SELL = "SIDE_SELL"

class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        {"schema": SQLServerConsts.ORDERS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.ORDERS_SCHEMA}].[{__tablename__}]"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid4()), index=True, nullable=False)
    account_id = Column(UNIQUEIDENTIFIER, ForeignKey(f"{SQLServerConsts.INVESTORS_SCHEMA}.accounts.id"), nullable=False)
    side = Column(SQLAlchemyEnum(OrderSide), nullable=False)
    symbol = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    order_quantity = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False)
    order_status = Column(SQLAlchemyEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    filled_quantity = Column(Integer, nullable=False)
    last_quantity = Column(Integer, nullable=False)
    error = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)