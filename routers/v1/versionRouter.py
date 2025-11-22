from .aiRouter import router as aiRouter
from .chatRouter import router as chatRouter
from .userRouter import router as userRouter
from fastapi import FastAPI

versionRouter = FastAPI()
versionRouter.include_router(chatRouter)
versionRouter.include_router(userRouter)
versionRouter.include_router(aiRouter)