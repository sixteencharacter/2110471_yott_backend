from sqlalchemy import UUID, Column, DateTime, func, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from .models import Base

class Message(Base):
    __tablename__ = "yott_message"

    mid = Column(Integer, primary_key=True, default=uuid.uuid4)
    data = Column(Text())
    s_id = Column(Text, ForeignKey("yott_person.uid")) #sender id
    cid = Column(Integer, ForeignKey("yott_chat.cid")) #chat id
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"id: {self.mid}, sender_id: {self.s_id}, timestamp: {self.timestamp}, chat_id: {self.cid}"