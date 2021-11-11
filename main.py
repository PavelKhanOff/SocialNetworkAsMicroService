from fastapi import FastAPI
from app.database import engine, Base
from app.middleware import middleware
from app.comments import comments
from app.posts import posts
from app.likes import likes
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from app.redis.redis import redis_cache


app = FastAPI(
    openapi_url="/feed/openapi.json", docs_url="/feed/docs", redoc_url="/feed/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comments.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(middleware.router)

# Base.metadata.create_all(engine)

add_pagination(app)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await redis_cache.init_cache()


@app.on_event("shutdown")
async def shutdown():
    await redis_cache.wait_closed()
