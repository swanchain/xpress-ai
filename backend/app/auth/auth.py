from datetime import datetime, timedelta
from typing import Optional
import time
import logging
import requests
import json
from jose import JWTError, jwt
from requests_oauthlib import OAuth1
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from config import settings
from app.database.session import get_db, get_one_object_by_filter
from constants import *

logger = logging.getLogger()

# Constants
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_id = int(user_id)
    user: User = await get_one_object_by_filter(db, User, x_user_id=user_id)
    
    if user is None:
        raise credentials_exception
    return user



def get_sign_message(wallet_address: str):
    rightnow = int(time.time())
    sortanow = rightnow - rightnow % 600
    current_time_period = datetime.fromtimestamp(sortanow).strftime("%Y-%m-%d %H:%M:%S")
    # current_time = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

    msg = f"""Welcome to Xpress AI. You are attempting to sign and log in to a page with the domain name https://{settings.DOMAIN}, please be careful to verify that. This request will not trigger a blockchain transaction or cost any gas fees. Your authentication status will reset after 24 hours. Wallet address: {wallet_address} Date: {current_time_period}"""

    return msg



"""X OAuth"""
def oauth_request_token():
    oauth = OAuth1(settings.X_API_KEY, client_secret=settings.X_API_KEY_SECRET)
    # Request
    params = {
        'oauth_callback': settings.X_OAUTH_CALLBACK
    }
    oauth_response = requests.post(REQUEST_TOKEN_URL, auth=oauth, params=params)
    return oauth_response


def oauth_user_verification(oauth_token: str, oauth_verifier: str):
    oauth = OAuth1(settings.X_API_KEY,
               client_secret=settings.X_API_KEY_SECRET,
               resource_owner_key=oauth_token,
               verifier=oauth_verifier)
    oauth_response = requests.post(OAUTH_ACCESS_TOKEN_URL, auth=oauth)
    return oauth_response

def decode_oauth_response(oauth_response: json):
    if oauth_response.status_code == 200:
        credentials = oauth_response.content.decode('utf-8')
        response_data = dict(x.split('=') for x in credentials.split('&'))
        return True, response_data
    return False, None
