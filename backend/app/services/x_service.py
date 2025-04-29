from typing import Optional, List
import tweepy
import os
import httpx
import logging
from dotenv import load_dotenv
from cachetools import TTLCache
from asyncache import cached
from constants import CACHE_TTL

load_dotenv()

logger = logging.getLogger()

cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)

@cached(cache)
async def get_user_tweets_history(
    x_user_id: Optional[int] = None,
    x_user_name: Optional[str] = None,
    max_history_count: int = 10,
) -> Optional[List[str]]:
    client = tweepy.Client(
        bearer_token=os.environ.get("X_BEARER_TOKEN_FOR_API"),
        wait_on_rate_limit=True
    )

    if not x_user_id and not x_user_name:
        raise ValueError("Either x_user_id or x_user_name must be provided")

    # get user id if not provided
    if not x_user_id:
        logger.info(f"Getting user id for {x_user_name}")
        user = client.get_user(username=x_user_name)
        if not user:
            return []
        x_user_id = user.data.id
        logger.info(f"User id for {x_user_name} is {x_user_id}")

    tweets = client.get_users_tweets(
        id=x_user_id,
        max_results=max_history_count,
        tweet_fields=["created_at", "public_metrics", "text", "entities", "id", "referenced_tweets"],
        expansions=["referenced_tweets.id", "referenced_tweets.id.author_id"]
    )

    if not tweets.data:
        return []

    return [tweet.text for tweet in tweets.data]

