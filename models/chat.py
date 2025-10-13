from sqlalchemy import Column, DateTime, String, Integer, func , Boolean
from .models import Base, message_belong_to_chat
from typing import List
from sqlalchemy.orm import relationship, Mapped
from .message import Message

class Chat(Base):
    __tablename__ = "yott_chat"

    cid = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)
    is_groupchat = Column(Boolean,default=False)

    messages: Mapped[List[Message]] = relationship(secondary=message_belong_to_chat)

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"