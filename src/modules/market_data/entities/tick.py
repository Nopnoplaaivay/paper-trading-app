from sqlalchemy import Column, DateTime, Integer, Float, String

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class Tick(Base):
    __tablename__ = 'tick'
    __table_args__ = (
        {"schema": SQLServerConsts.MARKET_DATA_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.MARKET_DATA_SCHEMA}].[{__tablename__}]"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    match_price = Column(Float)
    match_quantity = Column(Float)
    trading_time = Column(DateTime)
    side = Column(String)
    session = Column(String)