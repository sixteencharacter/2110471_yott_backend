from sqlalchemy import Column, DateTime, String, Integer, func , Boolean
from .models import Base

class Chat(Base):
    __tablename__ = "yott_chat"

    cid = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)
    is_groupchat = Column(Boolean,default=False)

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"