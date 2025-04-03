from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class Portfolios(Base):
    __tablename__ = "porfolios"
    __table_args__ = (
        UniqueConstraint("account_id", "symbol", name="uq_account_symbol"),
        {"schema": SQLServerConsts.INVESTORS_SCHEMA},
    )
    __sqlServerType__ = f"[{SQLServerConsts.INVESTORS_SCHEMA}].[{__tablename__}]"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    account_id = Column(UNIQUEIDENTIFIER, ForeignKey(f"{SQLServerConsts.INVESTORS_SCHEMA}.accounts.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    avg_price = Column(Integer, nullable=False, default=0)
    total_cost = Column(Integer, nullable=False, default=0)
    realized_profit = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
