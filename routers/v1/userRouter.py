from fastapi import APIRouter , Depends
from typing import Annotated
from fastapi.responses import JSONResponse
from utils import validate_access_token

router = APIRouter(prefix="/user",tags=["user"])

@router.get("/me")
async def get_all_available_chatroom(userData : Annotated[dict,Depends(validate_access_token)]):
    return JSONResponse(userData)

@router.get("/manifest")
async def get_all_available_chatroom(userData : Annotated[dict,Depends(validate_access_token)]):
    return JSONResponse({
        "sticker_set_owned" : []
    })