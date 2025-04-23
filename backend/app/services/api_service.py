import httpx
import logging

import requests
from fastapi import HTTPException
from constants import X_TWEET_POST_INFO_API

from config import settings

logger = logging.getLogger()

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
    tweet_id: str
):
    futurecitizen_x_api = settings.FUTURECITIZEN_X_GENERATE_REPLY_API
    futurecitizen_role_id = settings.FUTURECITIZEN_ROLE_ID
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
                "role_id": futurecitizen_role_id,
                "count": 1
            }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to generate reply, please check the tweet id")

    data = response.json()
    if 'replies' not in data or len(data['replies']) == 0:
        raise HTTPException(status_code=400, detail="Failed to generate reply, please check the tweet content")
    
    return data['replies'][0]['content']


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
