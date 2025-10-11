from sqlalchemy import Column, DateTime, String, Integer, func , UUID , Text
from .models import Base

class Person(Base):
    __tablename__ = "yott_person"

    uid = Column(UUID, primary_key=True)
    email = Column(Text(), unique=True)
    given_name = Column(Text(), unique=True)
    family_name = Column(Text(), unique=True)
    preferred_username = Column(Text(), unique=True)

    def __repr__(self):
        return f"id: {self.uid}, name: {self.given_name}"