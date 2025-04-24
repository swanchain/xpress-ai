from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import logging.config
from app.database.session import engine, create_tables
from config import settings, logging_config

from app.api import users, analyze

logging.config.dictConfig(logging_config)
logger = logging.getLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


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