# from app.worker.twitter_role_update import update_user_role_task
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import logging.config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from redis.asyncio import from_url
# from app.database.session import engine, create_tables
from config import settings, logging_config

from app.api import users, analyze, fine_tuning, ai_vibe, analyze_v2
from app.worker.generate_ai_vibe import update_user_ai_role


logging.config.dictConfig(logging_config)
logger = logging.getLogger()


scheduler = AsyncIOScheduler()

scheduler.add_job(
    update_user_ai_role, 
    "interval", 
    seconds=60,
    max_instances=1,
    replace_existing=False,
    next_run_time=datetime.now()
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await create_tables()
    redis_client = await from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis = redis_client
    scheduler.start()
    yield
    scheduler.shutdown()
    await redis_client.close()


app = FastAPI(lifespan=lifespan, title="XPressAI API")


origins = [
    "http://localhost:3000",    # TODO: remove
    f"https://{settings.DOMAIN}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    logger.debug("Welcome to XPressAI API")
    return {"message": "Welcome to XPressAI API"}

app.include_router(users.router)
app.include_router(analyze.router)
app.include_router(analyze_v2.router)
app.include_router(ai_vibe.router)
app.include_router(fine_tuning.router)
app.include_router(fine_tuning.router_for_tweets)