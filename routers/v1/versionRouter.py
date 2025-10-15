from .chatRouter import router as chatRouter
from .userRouter import router as userRouter
from .dataRouter import router as dataRouter
from fastapi import FastAPI

versionRouter = FastAPI()
versionRouter.include_router(chatRouter)
versionRouter.include_router(userRouter)
versionRouter.include_router(dataRouter, prefix="/api")