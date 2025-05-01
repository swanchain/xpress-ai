from pydantic_settings import BaseSettings

import os
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DOMAIN: str
    DEBUG: str
    REDIS_URL: str
    
    X_BEARER_TOKEN_FOR_API: str
    
    X_API_KEY: str
    X_API_KEY_SECRET: str
    X_BEARER_TOKEN: str
    X_OAUTH_CALLBACK: str

    
    FUTURECITIZEN_X_TWEET_CONTENT_API: str
    FUTURECITIZEN_X_GENERATE_REPLY_API: str
    FUTURECITIZEN_LOGIN_API: str
    FUTURECITIZEN_LOGIN_EMAIL: str
    FUTURECITIZEN_LOGIN_PSWD: str
    FUTURECITIZEN_ROLE_ID: int

    RPC: str
    CONTRACT_ADDRESS: str

    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignores extra environment variables


settings = Settings() 


import logging

log_level = logging.DEBUG if settings.DEBUG else logging.INFO


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,
            "backupCount": 5,
        },
    },
    "loggers": {
        "fastapi": {"handlers": ["console", "file"], "level": log_level},
        "uvicorn": {"handlers": ["console", "file"], "level": log_level},
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": log_level,
            "propagate": False,
        },
    },
    "root": {"handlers": ["console", "file"], "level": log_level},
}

