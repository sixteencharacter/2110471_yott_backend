from sqlalchemy import Column, UUID, ForeignKey, Integer
from .models import Base


class user_belong_to_chat(Base):
    __tablename__ = "yott_user_belong_to_chat"

    rid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("yott_person.uid"))
    cid = Column(Integer, ForeignKey("yott_chat.cid"))

    def __repr__(self):
        return f"id: {self.uid}, chat_id: {self.cid}"
