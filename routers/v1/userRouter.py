from fastapi import APIRouter , Depends
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from utils import validate_access_token , get_db
from models import Chat, user_belong_to_chat
from icecream import ic

router = APIRouter(prefix="/user",tags=["user"])

@router.get("/me")
async def get_all_available_chatroom(userData : Annotated[dict,Depends(validate_access_token)]):
    return JSONResponse(userData)

@router.get("/manifest")
async def get_all_available_chatroom(userData : Annotated[dict,Depends(validate_access_token)]):
    return JSONResponse({
        "sticker_set_owned" : []
    })

@router.get("/chats")
async def get_user_chats(userData : Annotated[dict,Depends(validate_access_token)], db : AsyncSession = Depends(get_db)):
    user_id = userData.get("sub")  # Use 'sub' which is the standard JWT claim for user ID
    # Join Chat and user_belong_to_chat tables to get user's chats
    result = await db.execute(
        select(Chat)
        .join(user_belong_to_chat, Chat.cid == user_belong_to_chat.cid)
        .where(user_belong_to_chat.uid == user_id)
    )
    
    chats = result.scalars().all()
    # print("Chats:", chats)
    
    # Convert to serializable format
    chat_list = []
    for chat in chats:
        chat_list.append({
            "cid": chat.cid,
            "name": chat.name,
            "is_groupchat": chat.is_groupchat
        })
    
    return JSONResponse(chat_list)