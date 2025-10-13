from sqlalchemy import Column, DateTime, String, Integer, func , UUID , Text
from .models import Base, user_belong_to_chat
from typing import List
from sqlalchemy.orm import relationship, Mapped
from .chat import Chat

class Person(Base):
    __tablename__ = "yott_person"

    uid = Column(UUID, primary_key=True)
    email = Column(Text())
    given_name = Column(Text())
    family_name = Column(Text())
    preferred_username = Column(Text())

    users: Mapped[List[Chat]] = relationship(secondary=user_belong_to_chat)

    def __repr__(self):
        return f"id: {self.uid}, name: {self.given_name}"