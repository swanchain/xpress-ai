
from typing import Optional 
from sqlalchemy import Integer, BigInteger, DECIMAL, String, Text, Enum, Boolean, JSON
from sqlalchemy.orm import mapped_column, Mapped

from app.database.session import Base

class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    wallet_address = mapped_column(String(42), unique=True, nullable=False)
    x_username = mapped_column(String(255), nullable=True)
    credit = mapped_column(DECIMAL(10, 2), nullable=False, default=0.00)
    created_at = mapped_column(BigInteger, nullable=False)
    updated_at = mapped_column(BigInteger, nullable=False)