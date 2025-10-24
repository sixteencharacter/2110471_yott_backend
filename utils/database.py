from services import sessionmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator , Any
import json
import datetime

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session

# this function takes any result and formed it back to dict
def populate_query_result(res : Any) -> Any :

    def serialize_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    column_names = list(res.keys())
    dat = res.all()
    payload = []
    for x in dat :
        payload.append(dict([[cname,d]for cname , d in zip(column_names,x)]))
    return json.loads(json.dumps(payload,default=serialize_datetime))
