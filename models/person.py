from sqlalchemy import Column, UUID, Integer , Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .models import Base
from sqlalchemy.orm import relationship

class Person(Base):
    __tablename__ = "yott_person"

    uid = Column(Text, primary_key=True)
    email = Column(Text())
    given_name = Column(Text())
    family_name = Column(Text())
    preferred_username = Column(Text())

    def __repr__(self):
        return f"id: {self.uid}, name: {self.given_name}"