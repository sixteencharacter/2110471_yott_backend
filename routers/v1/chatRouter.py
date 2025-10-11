from fastapi import APIRouter , Depends
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from utils import validate_access_token , get_db
from models import Chat
from icecream import ic

router = APIRouter(prefix="/chat",tags=["chat"])

@router.get("/")
async def get_all_available_chatroom(userData : Annotated[dict,Depends(validate_access_token)],db : AsyncSession = Depends(get_db)):
    chats = await db.execute(select(Chat))
    
    return JSONResponse(chats.all())