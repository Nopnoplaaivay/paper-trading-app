from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class Holdings(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint("account_id", "symbol", name="uq_account_symbol"),
        {"schema": SQLServerConsts.INVESTORS_SCHEMA},
    )
    __sqlServerType__ = f"[{SQLServerConsts.INVESTORS_SCHEMA}].[{__tablename__}]"

    id = Column(String, primary_key=True, index=True, nullable=False)
    symbol = Column(String(10), nullable=False)
    price = Column(Integer, nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=0)
    locked_quantity = Column(Integer, nullable=False, default=0)
    cost_basis_per_share = Column(Integer, nullable=False, default=0)
    account_id = Column(String, ForeignKey(f"{SQLServerConsts.INVESTORS_SCHEMA}.[accounts].[id]"), nullable=False)