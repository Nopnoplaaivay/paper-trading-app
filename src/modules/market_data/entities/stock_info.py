from sqlalchemy import Column, DateTime, Integer, Float, String

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class StockInfo(Base):
    __tablename__ = 'stock_info'
    __table_args__ = (
        {"schema": SQLServerConsts.MARKET_DATA_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.MARKET_DATA_SCHEMA}].[{__tablename__}]"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    floor_code = Column(String, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    trading_time = Column(DateTime)
    security_type = Column(String)
    ceiling_price = Column(Integer)
    floor_price = Column(Integer)
    highest_price = Column(Integer)
    lowest_price = Column(Integer)
    avg_price = Column(Integer)
    buy_foreign_quantity = Column(Integer)
    sell_foreign_quantity = Column(Integer)
    current_room = Column(Integer)
    accumulated_value = Column(Integer)
    accumulated_volume = Column(Integer)
    match_price = Column(Integer)
    match_quantity = Column(Integer)
    changed = Column(Float)
    changed_ratio = Column(Float)
    estimated_price = Column(Integer)
    trading_session = Column(String)
    security_status = Column(String)
    odd_lot_security_status = Column(String)
