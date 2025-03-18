from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from enum import Enum

from src.common.consts import SQLServerConsts
from src.modules.base.entities import Base


class Role(Enum):
    ADMIN = "admin"
    CLIENT = "client"
    BROKER = "broker"


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        {"schema": SQLServerConsts.ALPHA_RESULTS_SCHEMA},
        )
    __sqlServerType__ = f"[{SQLServerConsts.ALPHA_RESULTS_SCHEMA}].[{__tablename__}]"

    __id__ = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    account = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.CLIENT)
    type_broker = Column(String)
    type_client = Column(String)