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


router = APIRouter(prefix="/ai", tags=["AI Analyze"])

logger = logging.getLogger()

@router.post("/generate-tweet", response_model=dict)
async def generate_tweet(
    topic: str = Form(...),
    stance: Optional[str] = Form(None),
    additional_requirements: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not check_credits_enough(user):
        raise HTTPException(
            status_code=400, 
            detail="Not enough credits"
        )

    user_service = UserService(db)
    role = await user_service.get_user_role_details(user.id)
    if not role:
        role = settings.FUTURECITIZEN_ROLE_ID

    # Build system prompt
    system_prompt = (
        f"You are an AI assistant with the following configuration:\n"
        f"Name: {role.get('name', '')}\n"
        f"System Prompt: {role.get('system_prompt', '')}\n"
        f"Personality Traits: {', '.join(role.get('personality_traits', []))}\n"
        f"Background Story: {role.get('background_story', '')}\n"
        f"Category: {role.get('category', '')}\n"
        f"Language: {role.get('language', '')}\n\n"
        "You should build your personality framework with the above configuration and generate content according to the user's requirements."
        "Please respond in character, maintaining consistency with your configuration. "
        "Keep responses natural and engaging while staying true to your character."
        "The above configuration is just your personality framework, you should imitate the tone of voice through these personality frameworks, character, your answer does not need to be completely consistent with the config here, especially when the user's topic does not match his personality framework, you should try to imitate the user's tone of voice to generate content that matches the topic"
    )

    # Compose user prompt
    user_prompt = (
        f"Please generate a piece of content that can be sent to social media, with the TOPIC of the content being {topic},"
        f"the EMOTION of the content is {stance if stance else 'no specific emotion'},"
        f"the ADDITIONAL REQUIREMENTS of the content are {additional_requirements if additional_requirements else 'none' }."
    )

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                os.environ['NEBULA_GENERATE_REPLY_API'],
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ['NEBULA_API_KEY']}"
                }
            )
            response.raise_for_status()
            ai_result = response.json()
            tweet_content = ai_result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        logger.error(f"AI generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI generation failed")

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
async def generate_tweet_reply(
    tweet_url: str = Form(...),
    choose_sentiment: Optional[str] = Form(None),
    additional_context: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not check_credits_enough(user):
        raise HTTPException(
            status_code=400, 
            detail="Not enough credits"
        )

    user_service = UserService(db)
    role = await user_service.get_user_role_details(user.id)
    if not role:
        role = settings.FUTURECITIZEN_ROLE_ID

    # Get tweet content
    tweet_content = get_x_tweet_content(tweet_url)

    # Build system prompt (same as generate-tweet)
    system_prompt = (
        f"You are an AI assistant with the following configuration:\n"
        f"Name: {role.get('name', '')}\n"
        f"System Prompt: {role.get('system_prompt', '')}\n"
        f"Personality Traits: {', '.join(role.get('personality_traits', []))}\n"
        f"Background Story: {role.get('background_story', '')}\n"
        f"Category: {role.get('category', '')}\n"
        f"Language: {role.get('language', '')}\n\n"
        "You should build your personality framework with the above configuration and generate content according to the user's requirements."
        "Please respond in character, maintaining consistency with your configuration. "
        "Keep responses natural and engaging while staying true to your character."
        "The above configuration is just your personality framework, you should imitate the tone of voice through these personality frameworks, character, your answer does not need to be completely consistent with the config here, especially when the user's topic does not match his personality framework, you should try to imitate the user's tone of voice to generate content that matches the topic"
    )

    # Compose user prompt for reply
    user_prompt = (
        f"Please write a reply to the following tweet: '{tweet_content}'. "
        f"The sentiment of your reply should be: {choose_sentiment if choose_sentiment else 'no specific sentiment'}. "
        f"Additional context for your reply: {additional_context if additional_context else 'none'}."
    )

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                os.environ['NEBULA_GENERATE_REPLY_API'],
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ['NEBULA_API_KEY']}"
                }
            )
            response.raise_for_status()
            ai_result = response.json()
            reply_content = ai_result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        logger.error(f"AI generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI generation failed")

    if not reply_content:
        raise HTTPException(
            status_code=400, 
            detail="Invalid reply_content"
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