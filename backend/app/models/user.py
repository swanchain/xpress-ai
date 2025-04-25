
import time
from typing import Optional 
from sqlalchemy import Integer, BigInteger, DECIMAL, String, Text, Enum, Boolean, JSON
from sqlalchemy.orm import mapped_column, Mapped

from app.database.session import Base

class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid = mapped_column(String(255), unique=True, nullable=False)
    wallet_address = mapped_column(String(42), unique=True, nullable=True)
    x_user_id = mapped_column(BigInteger, unique=True, nullable=True)
    x_screen_name = mapped_column(String(255), unique=True, nullable=True)
    ai_role_id = mapped_column(Integer, nullable=True)
    credit = mapped_column(Integer, nullable=False, default=5)
    total_generated = mapped_column(Integer, nullable=False, default=0)
    created_at = mapped_column(BigInteger, nullable=False)
    updated_at = mapped_column(BigInteger, nullable=False)

    def to_dict(self):
        return {
            # "id": self.id,
            "uuid": self.uuid,
            # "wallet_address": self.wallet_address,
            # "x_user_id": self.x_user_id,
            "x_screen_name": self.x_screen_name,
            # "ai_role_id": self.ai_role_id,
            "free_credit_left": self.credit,
            "total_generated": self.total_generated,
            # "created_at": self.created_at,
            # "updated_at": self.updated_at,
        }