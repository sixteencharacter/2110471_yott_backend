#!/usr/bin/env python 
import config
import uvicorn
from fastapi import FastAPI,APIRouter, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import apiv1_router
from socket_server import socket_app
import requests
import jwt
import json


auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

@auth_router.get("/me")
async def get_current_user(authorization: str = Header(None)):
    """ดึงข้อมูล user จาก Keycloak token (วิธีง่ายๆ)"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        # Decode token โดยไม่ verify (สำหรับการทดสอบ - ในโปรดักชันควร verify)
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        return {
            "keycloak_id": decoded_token.get("sub"),
            "username": decoded_token.get("preferred_username"),
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "given_name": decoded_token.get("given_name"),
            "family_name": decoded_token.get("family_name"),
            "roles": decoded_token.get("realm_access", {}).get("roles", [])
        }
        
    except Exception as e:
        # ถ้า decode ไม่ได้ ลองใช้ Keycloak userinfo endpoint
        try:
            userinfo_url = "http://localhost:8080/realms/yott/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "keycloak_id": user_data.get("sub"),
                "username": user_data.get("preferred_username"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "given_name": user_data.get("given_name"),
                "family_name": user_data.get("family_name")
            }
            
        except Exception as inner_e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(inner_e)}")


























app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/v1",apiv1_router)
app.mount("/socket.io/",socket_app)
app.mount("/public",StaticFiles(directory="public"),name="public")

@app.get("/")
async def ping() :
    return "pong"

if __name__ == "__main__" :
    uvicorn.run("main:app",reload=True,reload_dirs=config.RELOAD_DIRS)
