#!/usr/bin/env python 
import config
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import apiv1_router

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

@app.get("/")
async def ping() :
    return "pong"

if __name__ == "__main__" :
    uvicorn.run("main:app",reload=True,reload_dirs=config.RELOAD_DIRS)
