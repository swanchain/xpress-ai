
from typing import Optional 
from sqlalchemy import Integer, BigInteger, DECIMAL, String, Text, Enum, Boolean, JSON
from sqlalchemy.orm import mapped_column, Mapped

from app.database.session import Base

class EvaluateHistory(Base):
    __tablename__ = 'evaluate_history'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_uuid = mapped_column(String(255), nullable=False)
    user_input = mapped_column(JSON, nullable=False)
    generated_text = mapped_column(Text, nullable=False)
    created_at = mapped_column(BigInteger, nullable=False)
    updated_at = mapped_column(BigInteger, nullable=False)
