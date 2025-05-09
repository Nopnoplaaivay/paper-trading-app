from sqlalchemy import Column, Integer, String, ForeignKey

from backend.common.consts import SQLServerConsts
from backend.modules.base.entities import Base



class Accounts(Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        {"schema": SQLServerConsts.INVESTORS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.INVESTORS_SCHEMA}].[{__tablename__}]"

    id = Column(String, primary_key=True, index=True, nullable=False)
    available_cash = Column(Integer, nullable=False)
    securing_amount = Column(Integer, nullable=False)
    purchasing_power = Column(Integer, nullable=False)
    user_id = Column(String, ForeignKey(f"{SQLServerConsts.AUTH_SCHEMA}.[users].[id]"), nullable=False)