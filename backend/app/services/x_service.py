from typing import Optional, List
import tweepy
import os
import httpx
import logging
from dotenv import load_dotenv
from redis.asyncio import Redis
import json
import hashlib

load_dotenv()

logger = logging.getLogger()

CACHE_TTL = 300  # Cache Time-to-Live in seconds, or use your constant

# Helper function to create a cache key based on user_id, user_name, and max_history_count
def generate_cache_key(
    x_user_id: Optional[int] = None, 
    x_user_name: Optional[str] = None, 
    max_history_count: int = 10
) -> str:
    if x_user_id:
        return f"user_tweets:{x_user_id}:{max_history_count}"
    if x_user_name:
        return f"user_tweets:{x_user_name}:{max_history_count}"
    return f"user_tweets:default:{max_history_count}"


async def get_user_tweets_history(
    x_user_id: Optional[int] = None,
    x_user_name: Optional[str] = None,
    max_history_count: int = 10,
    redis_client: Optional[Redis] = None
) -> Optional[List[str]]:
    
    if not x_user_id and not x_user_name:
        raise ValueError("Either x_user_id or x_user_name must be provided")

    # Create the cache key based on user id, username, and max_history_count
    cache_key = generate_cache_key(x_user_id, x_user_name, max_history_count)

    if redis_client:
        cached_tweets = await redis_client.get(cache_key)
        if cached_tweets:
            logger.info(f"Cache hit for {cache_key}")
            return json.loads(cached_tweets)

    # If not cached, fetch from Twitter API
    client = tweepy.Client(
        bearer_token=os.environ.get("X_BEARER_TOKEN_FOR_API"),
        wait_on_rate_limit=True
    )

    # Get user id if not provided
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

    tweet_texts = [tweet.text for tweet in tweets.data]

    if redis_client:
        await redis_client.setex(cache_key, CACHE_TTL, json.dumps(tweet_texts))
        logger.info(f"Cache set for {cache_key}")

    return tweet_texts
