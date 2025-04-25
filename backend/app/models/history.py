
from typing import Optional 
from sqlalchemy import Integer, BigInteger, DECIMAL, String, Text, Enum, Boolean, JSON
from sqlalchemy.orm import mapped_column, Mapped

from app.database.session import Base

class GenerateHistory(Base):
    __tablename__ = 'generate_history'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid = mapped_column(String(255), nullable=False)
    x_screen_name = mapped_column(String(255), nullable=False)
    generate_type = mapped_column(String(255), nullable=False)
    generated_text = mapped_column(Text, nullable=False)
    tweet_url = mapped_column(String(255), nullable=True)
    cost = mapped_column(Integer, nullable=True, default=1)
    created_at = mapped_column(BigInteger, nullable=False)
    updated_at = mapped_column(BigInteger, nullable=False)

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "generate_type": self.generate_type,
            "generated_text": self.generated_text,
            "tweet_url": self.tweet_url,
            "cost": self.cost,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }