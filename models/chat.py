from sqlalchemy import UUID, Column, String, Integer, Boolean
from .models import Base
from typing import List

class Chat(Base):
    __tablename__ = "yott_chat"

    cid = Column(Integer, primary_key=True)
    name = Column(String(60))
    is_groupchat = Column(Boolean,default=False)

    def __repr__(self):
        return f"id: {self.cid}, name: {self.name}"