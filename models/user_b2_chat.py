from sqlalchemy import Column, UUID, DateTime, ForeignKey, Integer, Text, func
from .models import Base


class user_belong_to_chat(Base):
    __tablename__ = "yott_user_belong_to_chat"

    rid = Column(Integer, primary_key=True)
    uid = Column(Text, ForeignKey("yott_person.uid"))
    cid = Column(Integer, ForeignKey("yott_chat.cid"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"id: {self.uid}, chat_id: {self.cid}, timestamp: {self.timestamp}"
