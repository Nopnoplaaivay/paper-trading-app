from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base

class Accounts(Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        {"schema": SQLServerConsts.AUTH_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.AUTH_SCHEMA}].[{__tablename__}]"

    account_id = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    total_cash = Column(Integer) # totalCash = availableCash + secureAmount + receivingAmount + 
    available_cash = Column(Integer) # availableCash = totalCash
    withdrawable_cash = Column(Integer) # withdrawableCash = availableCash - secureAmount
    stock_value = Column(Integer)
    total_debt = Column(Integer)
    net_asset_value = Column(Integer) # netAssetValue = stockValue + availableCash - totalDebt  
    securing_amount = Column(Integer)
    receiving_amount = Column(Integer)
    purchasing_power = Column(Integer)
    trading_token = Column(String)
    trading_token_exp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('Users', back_populates='accounts')