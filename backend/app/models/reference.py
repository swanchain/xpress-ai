
from typing import Optional 
from sqlalchemy import Integer, BigInteger, DECIMAL, String, Text, Enum, Boolean, JSON
from sqlalchemy.orm import mapped_column, Mapped

from app.database.session import Base

class PromptReference(Base):
    __tablename__ = 'prompt_reference'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref_url = mapped_column(Text, nullable=False)
