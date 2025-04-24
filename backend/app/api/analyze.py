import logging
from sqlalchemy.exc import IntegrityError
import httpx
import time
import secrets
import time
import traceback
from datetime import timedelta, datetime, timezone
from typing import Annotated, List, Dict, Optional
from urllib.parse import urlencode, urljoin

from eth_account.messages import encode_defunct
from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from web3.auto import w3

from app.auth.auth import get_current_user
from app.auth.auth import (
    create_access_token,
    get_sign_message,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from config import settings
from constants import OAUTH_AUTHORIZE
from app.database.session import get_db, get_one_object_by_filter
from app.schemas.user import (
    WalletSignatureLogin
)
from app.models.user import User
from app.services.api_service import (
    get_futurecitizen_bearer_token,
    get_x_task_reply,
    get_ai_role_id,
    get_x_tweet_id,
    get_x_tweet_content
)


router = APIRouter(prefix="/ai", tags=["AI Analyze"])

logger = logging.getLogger()

@router.post("/generate-tweet", response_model=dict)
async def generate_tweet(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    x_username = user.x_screen_name

    # if not x_username:
    #     raise HTTPException(
    #         status_code=400, 
    #         detail="Invalid x_username"
    #     )
    
    # x_history_content = get_x_history_content(x_username)

    # if not x_history_content:
    #     raise HTTPException(
    #         status_code=400, 
    #         detail="Invalid x_history_content"
    #     )
    
    # # call Futurecitizen API
    # futurecitizen_result = call_futurecitizen(x_history_content)

    return {
        "status": "success",
        "data": "under construction..."
    }

@router.post("/get-tweet-content", response_model=dict)
async def get_tweet_content(
    tweet_url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = get_x_tweet_content(tweet_url)
    return {
        "status": "Get tweet content successfully",
        "tweet_content": content
    }
    

@router.post("/generate-tweet-reply", response_model=dict)
async def analyze(
    tweet_url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    x_username = user.x_screen_name
    ai_role_id = user.ai_role_id if user.ai_role_id else settings.FUTURECITIZEN_ROLE_ID

    tweet_id = await get_x_tweet_id(tweet_url)

    reply_content = await get_x_task_reply(
        tweet_id,
        ai_role_id
    )

    return {
        "status": "Get reply content successfully",
        "reply_content": reply_content
    }