from sqlalchemy import Column, Integer, String, ForeignKey,  Enum as SQLAlchemyEnum
from enum import Enum

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class OrderSide(Enum):
    BUY = "SIDE_BUY"
    SELL = "SIDE_SELL"

class MatchOrders(Base):
    __tablename__ = 'match_orders'
    __table_args__ = (
        {"schema": SQLServerConsts.ORDERS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.ORDERS_SCHEMA}].[{__tablename__}]"

    id = Column(String, primary_key=True, index=True, nullable=False)
    account_id = Column(String, ForeignKey(f"{SQLServerConsts.INVESTORS_SCHEMA}.[accounts].[id]"), nullable=False)
    order_id = Column(String, ForeignKey(f"{SQLServerConsts.ORDERS_SCHEMA}.[orders].[id]"), nullable=False)
    side = Column(SQLAlchemyEnum(OrderSide), nullable=False)
    symbol = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False)