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
    create_prompt_input_for_reply_tweet,
    create_prompt_input_for_theme,
    create_prompt_input_for_evaluation
)
from app.services.api_service import (
    get_role_details_from_future_citizen
)

router = APIRouter(prefix="/ai/v2", tags=["AI Analyze V2"])

logger = logging.getLogger()


@router.post("/generate-theme-test-only", response_model=dict)
async def generate_theme(
    request: Request,
    choose_sentiment: Optional[str] = Form("Positive"),
    model_name_for_theme_generator: Optional[str] = Form("deepseek-ai/DeepSeek-V3-0324"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    redis_client = request.app.state.redis
    role_id = user.ai_role_id if user.ai_role_id else settings.FUTURECITIZEN_ROLE_ID
    role = await get_role_details_from_future_citizen(
        ai_role_id=role_id,
        redis_client=redis_client
    )
    
    if model_name_for_theme_generator and model_name_for_theme_generator not in ALL_AVAILABLE_MODEL_NAMES:
        raise HTTPException(
            status_code=400, 
            detail="Model name not supported"
        )

    if not model_name_for_theme_generator:
        model_name_for_theme_generator = "deepseek-ai/DeepSeek-V3-0324"

    payload = create_prompt_input_for_theme(
        role=role,
        choose_sentiment=choose_sentiment,
        model_name=model_name_for_theme_generator
    )

    theme_content = await request_llm(
        payload=payload,
    )

    return {
        "status": "Get theme successfully",
        "theme_content": theme_content,
        "user": user.to_dict(),
        "role": role
    }

@router.post("/generate-tweet", response_model=dict)
async def generate_tweet(
    request: Request,
    topic: str = Form(...),
    stance: Optional[str] = Form("Positive"),
    additional_requirements: Optional[str] = Form(None),
    model_name: Optional[str] = Form("meta-llama/Llama-3.3-70B-Instruct"),
    model_name_for_theme_generator: Optional[str] = Form("deepseek-ai/DeepSeek-V3-0324"),
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

    # if no additional requirements, use theme generation as additional context
    if not additional_requirements:

        if model_name_for_theme_generator and model_name_for_theme_generator not in ALL_AVAILABLE_MODEL_NAMES:
            raise HTTPException(
                status_code=400, 
                detail="Model name not supported"
            )

        if not model_name_for_theme_generator:
            model_name_for_theme_generator = "deepseek-ai/DeepSeek-V3-0324"

        try:
            additional_requirements_payload = create_prompt_input_for_theme(
                role=role,
                choose_sentiment=stance,
                model_name=model_name_for_theme_generator
            )

            additional_requirements = await request_llm(
                payload=additional_requirements_payload,
                model_name=model_name_for_theme_generator
            )
        except:
            additional_requirements = ""

    
    payload = create_prompt_input_for_tweet(
        role=role,
        topic=topic,
        stance=stance,
        additional_requirements=additional_requirements,
        model_name=model_name
    )

    tweet_content = await request_llm(
        payload=payload,
        model_name=model_name,
        # no redis for this request, no need to cache
        redis_client=None
    )

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


@router.post("/generate-tweet-reply", response_model=dict)
async def generate_tweet_reply(
    request: Request,
    tweet_url: str = Form(...),
    choose_sentiment: Optional[str] = Form("Positive"),
    additional_context: Optional[str] = Form(None),
    model_name: Optional[str] = Form("meta-llama/Llama-3.3-70B-Instruct"),
    model_name_for_theme_generator: Optional[str] = Form("deepseek-ai/DeepSeek-V3-0324"),
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


    # if no additional_context, use theme generation as additional context
    if not additional_context:

        if model_name_for_theme_generator and model_name_for_theme_generator not in ALL_AVAILABLE_MODEL_NAMES:
            raise HTTPException(
                status_code=400, 
                detail="Model name not supported"
            )

        if not model_name_for_theme_generator:
            model_name_for_theme_generator = "deepseek-ai/DeepSeek-V3-0324"

        try:
            additional_context_payload = create_prompt_input_for_theme(
                role=role,
                choose_sentiment=choose_sentiment,
                model_name=model_name_for_theme_generator
            )

            additional_context = await request_llm(
                payload=additional_context_payload,
                model_name=model_name_for_theme_generator
            )
        except:
            additional_context = ""


    payload = create_prompt_input_for_reply_tweet(
        role=role,
        tweet_content=tweet_content,
        choose_sentiment=choose_sentiment,
        additional_context=additional_context,
        model_name=model_name
    )

    reply_content = await request_llm(
        payload=payload,
        model_name=model_name,
        # no redis for this request, no need to cache
        redis_client=None
    )

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



@router.post("/evaluate-generated-tweet", response_model=dict)
async def eveluate_generated_tweet(
    request: Request,
    generated_content: str = Form(...),
    model_name_for_evaluator: Optional[str] = Form("deepseek-ai/DeepSeek-V3-0324"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    redis_client = request.app.state.redis
    
    role_id = user.ai_role_id if user.ai_role_id else settings.FUTURECITIZEN_ROLE_ID
    role = await get_role_details_from_future_citizen(
        ai_role_id=role_id,
        redis_client=redis_client
    )

    if model_name_for_evaluator and model_name_for_evaluator not in ALL_AVAILABLE_MODEL_NAMES:
        raise HTTPException(
            status_code=400, 
            detail="Model name not supported"
        )

    if not model_name_for_evaluator:
        model_name_for_evaluator = "deepseek-ai/DeepSeek-V3-0324"

    payload = create_prompt_input_for_evaluation(
        role=role,
        generated_content=generated_content,
        model_name=model_name_for_evaluator
    )

    evaluation_result = await request_llm(
        payload=payload,
        model_name=model_name_for_evaluator,
        # no redis for this request, no need to cache
        redis_client=None
    )

    return {
        "status": "Get evaluation result successfully",
        "evaluation-result": evaluation_result,
        "user": user.to_dict(),
        "role": role
    }


