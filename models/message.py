from sqlalchemy import Column, DateTime, String, Integer, func
from .models import Base
class Message(Base):
    __tablename__ = "yott_message"

    mid = Column(Integer, primary_key=True)
    s_id = Column(String(60), unique=True) #sender id
    data = Column(String(500))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"id: {self.id}, sender_id: {self.s_id}, timestamp: {self.timestamp}"