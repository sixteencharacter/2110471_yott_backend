#!/usr/bin/env python 
import config
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import apiv1_router
from socket_server import socket_app

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
