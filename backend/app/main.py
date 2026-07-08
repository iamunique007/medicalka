from fastapi import FastAPI

from app.models import Base

import redis.asyncio as redis

from app.db import async_engine

from app.config import RATE_LIMIT_REDIS_URL

from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth_router, post_router, comment_router, like_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(title="Medicalka API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router.router)
app.include_router(post_router.router)
app.include_router(like_router.router)
app.include_router(comment_router.router)