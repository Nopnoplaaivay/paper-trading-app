from sqlalchemy import Column, DateTime, Integer, Float, String

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class OHLC(Base):
    __tablename__ = 'ohlc'
    __table_args__ = (
        {"schema": SQLServerConsts.MARKET_DATA_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.MARKET_DATA_SCHEMA}].[{__tablename__}]"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    time = Column(String)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    last_updated = Column(String)
    stock_type = Column(String)