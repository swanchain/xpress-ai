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
from app.models.history import GenerateHistory
from app.models.reference import PromptReference
from app.services.api_service import (
    get_futurecitizen_bearer_token,
    get_x_task_reply,
    get_ai_role_id,
    get_x_tweet_id,
    get_x_tweet_content
)
from app.services.credit_service import check_credits_enough
from app.services.user_service import UserService

from app.services.llm_service import request_llm
from app.services.prompt_service import (
    create_prompt_input_for_tweet,
    create_prompt_input_for_reply_tweet
)
from app.services.api_service import (
    get_role_details_from_future_citizen
)

router = APIRouter(prefix="/ai", tags=["AI Analyze"])

logger = logging.getLogger()


@router.get("/get-all-available-model-names")
async def get_all_available_model_names():
    return {
        "status": "Get all available model names successfully",
        "model_names": ALL_AVAILABLE_MODEL_NAMES
    }

@router.post("/generate-tweet", response_model=dict)
async def generate_tweet(
    request: Request,
    topic: str = Form(...),
    stance: Optional[str] = Form(None),
    additional_requirements: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    redis_client = request.app.state.redis
    if not await check_credits_enough(user, redis_client):
        raise HTTPException(
            status_code=400, 
            detail="Not enough credits"
        )
    
    if model_name and model_name not in ALL_AVAILABLE_MODEL_NAMES:
        raise HTTPException(
            status_code=400, 
            detail="Model name not supported"
        )

    if not model_name:
        model_name = "meta-llama/Llama-3.3-70B-Instruct"

    role_id = user.ai_role_id if user.ai_role_id else settings.FUTURECITIZEN_ROLE_ID
    role = await get_role_details_from_future_citizen(
        ai_role_id=role_id,
        redis_client=redis_client
    )
    
    payload = create_prompt_input_for_tweet(
        role=role,
        topic=topic,
        stance=stance,
        additional_requirements=additional_requirements,
        model_name=model_name
    )

    tweet_content = await request_llm(payload)

    # update user credit
    user.total_generated = user.total_generated + 1
    user.updated_at = int(time.time())
    db.add(user)
    await db.commit()

    # update history
    history = GenerateHistory(
        uuid=user.uuid,
        x_screen_name=user.x_screen_name,
        generate_type=GENERATE_TYPE_TWEET,
        generated_text=tweet_content,
        tweet_url=None,
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    db.add(history)
    await db.commit()

    return {
        "status": "Get tweet content successfully",
        "tweet_content": tweet_content,
        "user": user.to_dict()
    }

@router.post("/get-tweet-content", response_model=dict)
async def get_tweet_content(
    request: Request,
    tweet_url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await get_x_tweet_content(
        tweet_url=tweet_url,
        redis_client=request.app.state.redis
    )
    
    return {
        "status": "Get tweet content successfully",
        "tweet_content": content
    }
    

@router.post("/generate-tweet-reply", response_model=dict)
async def generate_tweet_reply(
    request: Request,
    tweet_url: str = Form(...),
    choose_sentiment: Optional[str] = Form(None),
    additional_context: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    redis_client = request.app.state.redis
    if not await check_credits_enough(user, redis_client):
        raise HTTPException(
            status_code=400, 
            detail="Not enough credits"
        )
    
    if model_name and model_name not in ALL_AVAILABLE_MODEL_NAMES:
        raise HTTPException(
            status_code=400, 
            detail="Model name not supported"
        )
    
    if not model_name:
        model_name = "meta-llama/Llama-3.3-70B-Instruct"

    role_id = user.ai_role_id if user.ai_role_id else settings.FUTURECITIZEN_ROLE_ID
    role = await get_role_details_from_future_citizen(
        ai_role_id=role_id,
        redis_client=redis_client
    )

    tweet_content = await get_x_tweet_content(
        tweet_url=tweet_url,
        redis_client=request.app.state.redis
    )

    payload = create_prompt_input_for_reply_tweet(
        role=role,
        tweet_content=tweet_content,
        choose_sentiment=choose_sentiment,
        additional_context=additional_context,
        model_name=model_name
    )

    reply_content = await request_llm(payload)

    # update user credit
    user.total_generated = user.total_generated + 1
    user.updated_at = int(time.time())
    db.add(user)
    await db.commit()

    # update history
    history = GenerateHistory(
        uuid=user.uuid,
        x_screen_name=user.x_screen_name,
        generate_type=GENERATE_TYPE_REPLY,
        generated_text=reply_content,
        tweet_url=tweet_url,
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    db.add(history)
    await db.commit()

    return {
        "status": "Get reply content successfully",
        "reply_content": reply_content,
        "user": user.to_dict()
    }

@router.get("/get-generate-history")
async def get_generate_history(
    page: int = 1,
    size: int = 10,
    generate_type: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    offset = (page - 1) * size

    total_query = select(func.count()).select_from(GenerateHistory).filter(GenerateHistory.uuid == user.uuid)
    query = select(GenerateHistory).filter(GenerateHistory.uuid == user.uuid)

    if generate_type:
        total_query = total_query.filter(GenerateHistory.generate_type == generate_type)
        query = query.filter(GenerateHistory.generate_type == generate_type)

    total_result = await db.execute(total_query)
    total = total_result.scalar_one_or_none() or 0
    query_result = await db.execute(query.offset(offset).limit(size))
    result = query_result.scalars().all()

    return {
        "status": "Get generate history successfully",
        "total": total,
        "histories": result,
        "page": page,
        "size": len(result)
    }