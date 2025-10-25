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
    # print("User Data:", userData)
    chats = await db.execute(select(Chat))

    return JSONResponse(chats.all())

@router.get("/{chatId}/members")
async def list_chat_member(chatId : str,userData : Annotated[dict,Depends(validate_access_token)],db : AsyncSession = Depends(get_db)) :
    query = """
        select P.uid , P.given_name , P.family_name , preferred_username from yott_user_belong_to_chat R
        join yott_person P on R.uid = P.uid
        where cid = :chatId
    """
    members = await db.execute(text(query),{"chatId" : int(chatId)})
    return JSONResponse(populate_query_result(members))

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
