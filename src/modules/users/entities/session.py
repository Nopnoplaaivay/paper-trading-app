from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
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

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=lambda: str(uuid4()).lower(), index=True, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    role = Column(String)
    user_id = Column(Integer, ForeignKey(f'[{SQLServerConsts.AUTH_SCHEMA}].[user].[id]', ondelete='CASCADE'), nullable=False)
    # user = relationship('users', back_populates='sessions')