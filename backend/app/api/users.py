import logging
import os
from sqlalchemy.exc import IntegrityError
import httpx
import time
import secrets
import uuid
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
import tweepy
from tweepy.errors import TooManyRequests

from app.auth.auth import get_current_user
from app.auth.auth import (
    create_access_token,
    get_sign_message,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from config import settings
from constants import *
from app.database.session import get_db, get_one_object_by_filter
from app.schemas.user import (
    WalletSignatureLogin
)
from app.models.user import User
from app.services.user_service import UserService
from app.auth.auth import oauth_request_token, oauth_user_verification, decode_oauth_response

router = APIRouter(prefix="/user", tags=["User"])

logger = logging.getLogger()


@router.get("/x_oauth_login", response_model=dict)
async def x_oauth_login():
    try:
        oauth_response = oauth_request_token()
        oauth_status, oauth_response_data = decode_oauth_response(oauth_response)
        
        if oauth_status:
            oauth_token = oauth_response_data['oauth_token']
            oauth_token_secret = oauth_response_data['oauth_token_secret']
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "OAuth token generated successfully. (Expires in 5 minutes)",
                    "data": {
                        "oauth_token": oauth_token,
                        "oauth_token_secret": oauth_token_secret,
                        "authorized_url": f"{OAUTH_AUTHORIZE}?oauth_token={oauth_token}"
                    }
                }
            )
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "OAuth token generation failed."
                }
            )
    except Exception as e:
        logging.error(f"OAuth Login Failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.post("/login_x_account")
async def login_x_account(
    oauth_token: str = Form(...), 
    oauth_verifier: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    oauth_response = oauth_user_verification(
        oauth_token=oauth_token, 
        oauth_verifier=oauth_verifier
    )
    oauth_status, oauth_response_data = decode_oauth_response(oauth_response)
    
    if not oauth_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth token expired."
        )
    
    x_user_id = int(oauth_response_data['user_id'])
    x_screen_name = oauth_response_data['screen_name']

    user: User = await get_one_object_by_filter(db, User, x_user_id=x_user_id)
    if user:
        logging.info("[+] Found user " + user.x_screen_name)
    else:
        user = User(
            uuid=str(uuid.uuid4()),
            x_user_id=x_user_id,
            x_screen_name=x_screen_name,
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.x_user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    res = {
        "access_token": access_token, 
        "token_type": "Bearer",
        "user": user.to_dict()
    }
    return res


@router.get("/get-user", response_model=dict)
async def generate_tweet(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {
        "status": "Get user successfully",
        "user": user.to_dict()
    }


@router.post("/get-user-tweets-history")
async def get_user_tweets_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        client = tweepy.Client(
            bearer_token=os.environ.get("X_BEARER_TOKEN_FOR_API"),
            wait_on_rate_limit=True
        )
        user_service = UserService(db)
        tweets = await user_service.get_user_tweets(
            client=client,
            user_id=user.x_user_id,
            max_results=5
        )
        
        if not tweets:
            return {
                "status": "No tweets found",
                "tweets": []
            }
            
        return {
            "status": "Get user tweets successfully",
            "tweets": [{"text": tweet.text, "created_at": tweet.created_at} for tweet in tweets]
        }
        
    except TooManyRequests:
        raise HTTPException(
            status_code=429,
            detail="You are running out of credit or the system is busy, please try it again."
        )
    except Exception as e:
        logging.error(f"Error getting user tweets: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="You are running out of credit or the system is busy, please try it again."
        )
    
@router.get("/get-user-role-details", response_model=dict)
async def get_user_role_details(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the role details for the current user
    """
    try:
        user_service = UserService(db)
        role_details = await user_service.get_user_role_details(user.id)
        
        if not role_details:
            raise HTTPException(
                status_code=404,
                detail="Role details not found"
            )
            
        return role_details
        
    except Exception as e:
        logger.error(f"Error getting role details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get role details"
        )


# @router.post("/get-wallet-sign-message")
# async def get_wallet_sign_message_for_login_directly_by_wallet(
#     wallet_address: str, 
#     db: AsyncSession = Depends(get_db),
# ):
#     if not wallet_address:
#         raise HTTPException(
#             status_code=400, 
#             detail="Invalid wallet address"
#         )
#     return {
#             "status": "success",
#             "data": get_sign_message(wallet_address=wallet_address)
#         }


# @router.post("/login-by-wallet")
# async def login_directly_by_wallet(
#     wallet_signature_login: WalletSignatureLogin,
#     db: AsyncSession = Depends(get_db),
# ):
#     wallet_address = wallet_signature_login.wallet_address
#     signature = wallet_signature_login.signature
    
#     original_message = get_sign_message(wallet_address)
#     logging.debug(f"{original_message=}")
#     logging.debug(f"{wallet_address=}")
#     logging.debug(f"{signature=}")
#     message_hash = encode_defunct(text=original_message)
#     signer = w3.eth.account.recover_message(message_hash, signature=signature)
#     logging.info(signer + " signed the message")

#     if signer == wallet_address:
#         user: User = await get_one_object_by_filter(db, User, wallet_address=wallet_address)
#         if user:
#             logging.info("[+] Found user " + user.wallet_address)
#         else:
#             user = User(
#                 wallet_address=wallet_address,
#                 created_at=int(time.time()),
#                 updated_at=int(time.time())
#             )
#             db.add(user)
#             await db.commit()
#             await db.refresh(user)
#     else:
#         raise HTTPException(status_code=401, detail='could not authenticate signature')

#     access_token = create_access_token(
#         data={"sub": str(user.user_id)},
#         expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     )
    
#     res = {"access_token": access_token, "token_type": "Bearer"}
#     return res
    
