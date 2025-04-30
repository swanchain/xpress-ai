import httpx
import logging
import os
import requests
from fastapi import HTTPException
from constants import X_TWEET_POST_INFO_API
from constants import CACHE_TTL
from cachetools import TTLCache
from asyncache import cached

from dotenv import load_dotenv

from config import settings

load_dotenv()

logger = logging.getLogger()

cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)

def get_futurecitizen_bearer_token():
    futurecitizen_x_api = settings.FUTURECITIZEN_LOGIN_API

    response = requests.post(
        futurecitizen_x_api,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json={
            "email": settings.FUTURECITIZEN_LOGIN_EMAIL,
            "password": settings.FUTURECITIZEN_LOGIN_PSWD
        }
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to login Futurecitizen")
    else:
        data = response.json()
        if 'access_token' not in data:
            raise HTTPException(status_code=500, detail="Failed to get token from Futurecitizen")
        else:
            return data['access_token']


async def get_futurecitizen_bearer_token_async():
    futurecitizen_x_api = settings.FUTURECITIZEN_LOGIN_API

    async with httpx.AsyncClient() as client:
        response = await client.post(
            futurecitizen_x_api,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json={
                "email": settings.FUTURECITIZEN_LOGIN_EMAIL,
                "password": settings.FUTURECITIZEN_LOGIN_PSWD
            }
        )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to login Futurecitizen")
    else:
        data = response.json()
        if 'access_token' not in data:
            raise HTTPException(status_code=500, detail="Failed to get token from Futurecitizen")
        else:
            return data['access_token']


async def get_x_tweet_id(
    tweet_url: str
):
    futurecitizen_x_api = settings.FUTURECITIZEN_X_TWEET_CONTENT_API
    futurecitizen_bear_token = await get_futurecitizen_bearer_token_async()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            futurecitizen_x_api,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {futurecitizen_bear_token}"
            },
            json={
                "tweet_url": tweet_url,
                "twitter_account_id": 0
            }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get tweet id, please check the tweet url")

    data = response.json()
    return data['tweet_id']


async def get_ai_role_id(
    tweet_url: str
):
    futurecitizen_x_api = settings.FUTURECITIZEN_X_TWEET_CONTENT_API
    futurecitizen_bear_token = await get_futurecitizen_bearer_token_async()
    
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         futurecitizen_x_api,
    #         headers={
    #             "accept": "application/json",
    #             "Authorization": f"Bearer {futurecitizen_bear_token}"
    #         },
    #         json={
    #             "tweet_url": tweet_url,
    #             "twitter_account_id": 0
    #         }
    #     )

    # if response.status_code != 200:
    #     raise HTTPException(status_code=400, detail="Failed to get tweet id, please check the tweet url")

    # data = response.json()
    # return data['tweet_id']
    return 10



async def get_x_task_reply(
    tweet_id: str,
    ai_role_id: int
):
    futurecitizen_x_api = settings.FUTURECITIZEN_X_GENERATE_REPLY_API
    futurecitizen_bear_token = await get_futurecitizen_bearer_token_async()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            futurecitizen_x_api,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {futurecitizen_bear_token}"
            },
            json={
                "tweet_id": tweet_id,
                "role_id": ai_role_id,
                "count": 1
            }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to generate reply, please check the tweet id")

    data = response.json()
    if 'replies' not in data or len(data['replies']) == 0:
        raise HTTPException(status_code=400, detail="Failed to generate reply, please check the tweet content")
    
    return data['replies'][0]['content']

@cached(cache)
def get_x_tweet_content(
    tweet_url: str
):
    futurecitizen_x_api = settings.FUTURECITIZEN_X_TWEET_CONTENT_API
    futurecitizen_bear_token = get_futurecitizen_bearer_token()
    
    response = requests.post(
        futurecitizen_x_api,
        headers={
            "accept": "application/json",
            "Authorization": f"Bearer {futurecitizen_bear_token}"
        },
        json={
            "tweet_url": tweet_url,
            "twitter_account_id": 0
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get tweet content, please check the tweet url")

    data = response.json()
    return data['tweet_content']


async def send_role_to_future_citizen(
    payload: dict
):
    # Get bearer token through login
    bearer_token = await get_futurecitizen_bearer_token_async()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            os.environ['FUTURECITIZEN_CREATE_ROLE_API'],
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {bearer_token}",
                "accept": "application/json, text/plain, */*"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        try:
            return str(result['id'])
        except KeyError as e:
            raise ValueError("Role ID not found in API response") from e


async def get_role_details_from_future_citizen(
    ai_role_id: str
):
    bearer_token = await get_futurecitizen_bearer_token_async()
    
    # Make API call to get role details
    async with httpx.AsyncClient() as client:
        response = await client.get(
            os.environ['FUTURECITIZEN_GET_USER_ROLE_DETAIL'] + f"/{ai_role_id}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {bearer_token}"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get role details: {response.text}")
            return None
            
        return response.json()
        