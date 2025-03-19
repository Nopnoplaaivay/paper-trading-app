from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base



class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        {"schema": SQLServerConsts.AUTH_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.AUTH_SCHEMA}].[{__tablename__}]"

    id = Column(String, primary_key=True, index=True, nullable=False)
    signature = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('Users', back_populates='sessions')