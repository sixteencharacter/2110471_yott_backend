from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

message_belong_to_chat = Table(
    "message_belong_to",
    Base.metadata,
    Column("message_id", ForeignKey("yott_message.mid")),
    Column("chat_id", ForeignKey("yott_chat.cid")),
)

user_belong_to_chat = Table(
    "user_belong_to",
    Base.metadata,
    Column("user_id", ForeignKey("yott_person.uid")),
    Column("chat_id", ForeignKey("yott_chat.cid")),
)