from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from uuid import uuid4

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base



class Accounts(Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        {"schema": SQLServerConsts.INVESTORS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.INVESTORS_SCHEMA}].[{__tablename__}]"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid4()).lower(), index=True, nullable=False)
    total_cash = Column(Integer, nullable=False)
    available_cash = Column(Integer, nullable=False)
    withdrawable_cash = Column(Integer, nullable=False)
    stock_value = Column(Integer, nullable=False)
    total_debt = Column(Integer, nullable=False)
    net_asset_value = Column(Integer, nullable=False)
    securing_amount = Column(Integer, nullable=False)
    receiving_amount = Column(Integer, nullable=False)
    purchasing_power = Column(Integer, nullable=False)
    user_id = Column(UNIQUEIDENTIFIER, ForeignKey(f"{SQLServerConsts.AUTH_SCHEMA}.[users].[id]"), nullable=False)