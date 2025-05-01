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

from config import settings
from app.services.api_service import (
    get_x_tweet_content
)
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
    send_role_to_future_citizen
)

router = APIRouter(prefix="/fine-tuning", tags=["Fine Tuning"])
router_for_tweets = APIRouter(prefix="/fine-tuning-for-tweets", tags=["Fine Tuning For Tweets"])

logger = logging.getLogger()


@router.get("/x-user-tweets-history", response_model=dict)
async def get_x_user_tweets_history(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )
    return {
        "status": "Get user tweets successfully",
        "user_tweets": user_tweets
    }


@router.get("/get-prompt-for-user-role-data", response_model=dict)
async def get_prompt_for_user_role_data(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    return {
        "status": "Get ai role prompt template successfully",
        "prompt": prompt
    }

@router.post("/request-llm-for-user-role-data", response_model=dict)
async def request_llm_for_user_role_data(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    role_data = await request_llm(
        payload=prompt,
        redis_client=request.app.state.redis
    )

    return {
        "status": "Get user's ai role data successfully",
        "user_role_data_raw": role_data
    }


@router.post("/preview-future-citizen-role-input", response_model=dict)
async def preview_future_citizen_role_input(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    role_data = await request_llm(
        payload=prompt,
        redis_client=request.app.state.redis
    )

    future_citizen_role_input = create_future_citizen_role_input(
        user_role_data=role_data
    )

    return {
        "status": "Get future citizen role input successfully",
        "future_citizen_role_input": future_citizen_role_input
    }

@router.post("/placeholder-save-role-to-future-citizen", response_model=dict)
async def placeholder_save_role_to_future_citizen(
    x_user_name: str,
    max_history_count: Optional[int] = 10
):
    return {
        "status": "This API will save role to future citizen successfully",
        "role_id": "The returned role id (for demo purposes, no need for fine-tuning)"
    }


@router_for_tweets.post("/preview-prompt-for-tweet", response_model=dict)
async def preview_prompt_for_tweet(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10,
    topic: str = Form(...),
    stance: Optional[str] = Form(None, description="positive, negative, neutral"),
    additional_requirements: Optional[str] = Form(None, description="additional requirements")
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    role_data = await request_llm(
        payload=prompt,
        redis_client=request.app.state.redis
    )

    future_citizen_role_input = create_future_citizen_role_input(
        user_role_data=role_data
    )

    payload = create_prompt_input_for_tweet(
        role=future_citizen_role_input,
        topic=topic,
        stance=stance,
        additional_requirements=additional_requirements
    )

    return {
        "status": "Get prompt for tweet successfully",
        "preview-prompt-payload": payload,
    }


@router_for_tweets.post("/request-llm-for-tweet", response_model=dict)
async def request_llm_for_tweet(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10,
    topic: str = Form(...),
    stance: Optional[str] = Form(None, description="positive, negative, neutral"),
    additional_requirements: Optional[str] = Form(None, description="additional requirements")
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    role_data = await request_llm(
        payload=prompt,
        redis_client=request.app.state.redis
    )

    future_citizen_role_input = create_future_citizen_role_input(
        user_role_data=role_data
    )

    # for demo only, so no role saving
    
    if not topic:
        topic = "lifehack"

    payload = create_prompt_input_for_tweet(
        role=future_citizen_role_input,
        topic=topic,
        stance=stance,
        additional_requirements=additional_requirements
    )

    tweet = await request_llm(
        payload=payload,
        # redis_client=request.app.state.redis
    )

    return {
        "status": "Generate tweet successfully",
        "tweet": tweet
    }



@router_for_tweets.post("/preview-prompt-for-reply-tweet", response_model=dict)
async def preview_prompt_for_reply_tweet(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10,
    tweet_url: str = Form(...),
    stance: Optional[str] = Form(None, description="positive, negative, neutral"),
    additional_requirements: Optional[str] = Form(None, description="additional requirements")
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    role_data = await request_llm(
        payload=prompt,
        redis_client=request.app.state.redis
    )

    future_citizen_role_input = create_future_citizen_role_input(
        user_role_data=role_data
    )

    # for demo only, so no role saving

    tweet_content = get_x_tweet_content(
        tweet_url=tweet_url,
        redis_client=request.app.state.redis
    )

    payload = create_prompt_input_for_reply_tweet(
        role=future_citizen_role_input,
        tweet_content=tweet_content,
        choose_sentiment=stance,
        additional_context=additional_requirements
    )


    return {
        "status": "Get prompt for tweet successfully",
        "preview-prompt-payload": payload
    }


@router_for_tweets.post("/request-llm-for-reply-tweet", response_model=dict)
async def request_llm_for_reply_tweet(
    request: Request,
    x_user_name: str,
    max_history_count: Optional[int] = 10,
    tweet_url: str = Form(...),
    stance: Optional[str] = Form(None, description="positive, negative, neutral"),
    additional_requirements: Optional[str] = Form(None, description="additional requirements")
):
    user_tweets = await get_user_tweets_history(
        x_user_id=None,
        x_user_name=x_user_name,
        max_history_count=max_history_count,
        redis_client=request.app.state.redis
    )

    prompt = create_prompt_for_user_role_data(
        tweets=user_tweets
    )

    role_data = await request_llm(
        payload=prompt,
        redis_client=request.app.state.redis
    )

    future_citizen_role_input = create_future_citizen_role_input(
        user_role_data=role_data
    )

    # for demo only, so no role saving

    tweet_content = get_x_tweet_content(
        tweet_url=tweet_url,
        redis_client=request.app.state.redis
    )

    payload = create_prompt_input_for_reply_tweet(
        role=future_citizen_role_input,
        tweet_content=tweet_content,
        choose_sentiment=stance,
        additional_context=additional_requirements
    )

    reply_tweet = await request_llm(
        payload=payload,
        # redis_client=request.app.state.redis
    )

    return {
        "status": "Generate tweet successfully",
        "reply_tweet": reply_tweet
    }