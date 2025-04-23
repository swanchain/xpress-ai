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


router = APIRouter(prefix="/user", tags=["authentication"])

logger = logging.getLogger()

@router.post("/get-wallet-sign-message")
async def get_wallet_sign_message_for_login_directly_by_wallet(
    wallet_address: str, 
    db: AsyncSession = Depends(get_db),
):
    if not wallet_address:
        raise HTTPException(
            status_code=400, 
            detail="Invalid wallet address"
        )
    return {
            "status": "success",
            "data": get_sign_message(wallet_address=wallet_address)
        }


@router.post("/login-by-wallet")
async def login_directly_by_wallet(
    wallet_signature_login: WalletSignatureLogin,
    db: AsyncSession = Depends(get_db),
):
    wallet_address = wallet_signature_login.wallet_address
    signature = wallet_signature_login.signature
    
    original_message = get_sign_message(wallet_address)
    logging.debug(f"{original_message=}")
    logging.debug(f"{wallet_address=}")
    logging.debug(f"{signature=}")
    message_hash = encode_defunct(text=original_message)
    signer = w3.eth.account.recover_message(message_hash, signature=signature)
    logging.info(signer + " signed the message")

    if signer == wallet_address:
        user: User = await get_one_object_by_filter(db, User, wallet_address=wallet_address)
        if user:
            logging.info("[+] Found user " + user.wallet_address)
        else:
            user = User(
                wallet_address=wallet_address,
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
    else:
        raise HTTPException(status_code=401, detail='could not authenticate signature')

    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    res = {"access_token": access_token, "token_type": "Bearer"}
    return res
    
