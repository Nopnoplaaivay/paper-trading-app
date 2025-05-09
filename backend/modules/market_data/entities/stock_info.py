from sqlalchemy import Column, DateTime, Integer, Float, String

from backend.common.consts import SQLServerConsts
from backend.modules.base.entities import Base


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
    ceiling_price = Column(Float)
    floor_price = Column(Float)
    highest_price = Column(Float)
    lowest_price = Column(Float)
    avg_price = Column(Float)
    buy_foreign_quantity = Column(Float)
    sell_foreign_quantity = Column(Float)
    current_room = Column(Float)
    accumulated_value = Column(Float)
    accumulated_volume = Column(Float)
    match_price = Column(Float)
    match_quantity = Column(Float)
    changed = Column(Float)
    changed_ratio = Column(Float)
    estimated_price = Column(Float)
    trading_session = Column(String)
    security_status = Column(String)
    odd_lot_security_status = Column(String)
