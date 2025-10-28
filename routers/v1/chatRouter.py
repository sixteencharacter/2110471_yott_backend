from fastapi import APIRouter , Depends , Query
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , text
from utils import validate_access_token , get_db , populate_query_result
from models import Chat
from icecream import ic


router = APIRouter(prefix="/chats",tags=["chat"])

@router.get("/")
async def get_all_available_chatroom(userData : Annotated[dict,Depends(validate_access_token)],db : AsyncSession = Depends(get_db)):
    chats = await db.execute(select(Chat))
    result = chats.scalars().all()
    # Convert to serializable format
    chat_list = []
    for chat in result:
        chat_list.append({
            "cid": chat.cid,
            "name": chat.name,
            "is_groupchat": chat.is_groupchat
        })
    return JSONResponse(chat_list)

@router.get("/{chatId}/history")
async def list_chat_history(
    chatId : str ,
    userData : Annotated[dict,Depends(validate_access_token)],
    limit : int = 10,
    skip : int = 0,
    db : AsyncSession = Depends(get_db)) :
    query = """
        select P.uid , P.given_name , P.family_name , P.preferred_username , M.data as msg_content , M."timestamp"
        from yott_message M
        join yott_person P on M.s_id = P.uid
        where cid = :chatId order by M."timestamp" DESC
        OFFSET :skip
        LIMIT :limit
    """
    messages = await db.execute(text(query),{"chatId" : int(chatId),"skip" : skip , "limit" : limit})
    return JSONResponse(populate_query_result(messages))
