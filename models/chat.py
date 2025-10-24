from sqlalchemy import UUID, Column, DateTime, String, Integer, Boolean, func
from .models import Base
from typing import List

class Chat(Base):
    __tablename__ = "yott_chat"

    cid = Column(Integer, primary_key=True)
    name = Column(String(60))
    is_groupchat = Column(Boolean,default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"id: {self.cid}, name: {self.name}, timestamp: {self.timestamp}"