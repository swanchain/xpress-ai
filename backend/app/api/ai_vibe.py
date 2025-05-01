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
import os
from redis.asyncio import Redis

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
from constants import *
from constants import OAUTH_AUTHORIZE
from app.database.session import get_db, get_one_object_by_filter, get_all_objects_by_filter
from app.schemas.user import (
    WalletSignatureLogin
)
from app.models.user import User

from app.services.x_service import (
    get_user_tweets_history
)
from app.services.prompt_service import (
    create_prompt_for_user_role_data,
    create_future_citizen_role_input,
    create_prompt_input_for_tweet,
    create_prompt_input_for_reply_tweet
)
from app.services.llm_service import (
    request_llm
)
from app.services.api_service import (
    send_role_to_future_citizen,
    get_role_details_from_future_citizen
)
from app.tasks.ai_vibe import refresh_user_vibe_task

router = APIRouter(prefix="/ai-vibe", tags=["AI Vibe"])

logger = logging.getLogger()


@router.post('/refresh-my-vibe')
async def refresh_my_vibe(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    x_user_name = user.x_screen_name
    x_user_id = user.x_user_id
    max_history_count = 10
    try:
        user_tweets = await get_user_tweets_history(
            x_user_id=x_user_id,
            x_user_name=x_user_name,
            max_history_count=max_history_count
        )
    except:
        raise HTTPException(
            status_code=404,
            detail="X API is being rate limited. Please try again later"
        )
    
    try:

        prompt = create_prompt_for_user_role_data(
            tweets=user_tweets
        )

        role_data = await request_llm(prompt)
    
    except Exception as e:
        logger.error(f"Error getting role data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get role data. Please try again later"
        )

    try:
        future_citizen_role_input = create_future_citizen_role_input(
            user_role_data=role_data,
            x_user_id=user.x_user_id,
            x_user_name=x_user_name,
        )

        ai_role_id = await send_role_to_future_citizen(
            payload=future_citizen_role_input
        )

        user.ai_role_id = ai_role_id
        db.add(user)
        await db.commit()

    except Exception as e:
        logger.error(f"Error sending role to future citizen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save role. Please try again later"
        )

    try:

        role_details = await get_role_details_from_future_citizen(
            ai_role_id=ai_role_id
        )

        if not role_details:
            raise HTTPException(
                status_code=404,
                detail="Role vibe details not available. Please try again later"
            )
        return role_details
    
    except Exception as e:
        logger.error(f"Error getting role details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get role details. Please try again later"
        )


@router.post('/refresh-my-vibe-async')
async def refresh_my_vibe_background(
    user: User = Depends(get_current_user)
):
    refresh_user_vibe_task.delay(user.id)
    return {"detail": "AI Character refresh started. Please check back later."}



@router.post('/refresh-my-vibe-async-test')
async def refresh_my_vibe_background_(
    user_id: int
):
    refresh_user_vibe_task.delay(user_id)
    return {"detail": "AI Character refresh started. Please check back later."}