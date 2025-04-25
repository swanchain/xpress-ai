import tweepy
import dotenv
import os
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from ..models.user import User
from ..database.session import get_engine
from tweepy.errors import TooManyRequests
import httpx

logger = logging.getLogger(__name__)

async def get_user_tweets(client: tweepy.Client, user_id: int) -> str:
    """
    Get user's tweets
    """
    tweets = client.get_users_tweets(
        id=user_id,
        max_results=10,
        tweet_fields=["created_at", "public_metrics", "text", "entities", "id", "referenced_tweets"],
        expansions=["referenced_tweets.id", "referenced_tweets.id.author_id"]
    )
    
    if not tweets.data:
        logger.info(f"No tweets found for user ID: {user_id}")
        return None
        
    return tweets.data

async def analyze_tweets_with_llm(tweets: str) -> str:
    """
    Call LLM to analyze user's tweets
    """
    pass

async def create_future_citizen_role(user_data: Dict[str, Any]) -> str:
    """
    Call FutureCitizen API to create role
    """
    pass

async def update_user_role(user: User, role_id: str) -> None:
    """
    Update user's role_id
    """
    user.update_user_role_by_user_id(user.id, role_id)
    logger.info(f"Successfully updated role_id for user {user.id}")

async def process_single_user(client: tweepy.Client, user: User) -> None:
    """
    Process the complete process for a single user
    """
    # 1. Get user's tweets
    tweets = await get_user_tweets(client, user.x_user_id)
    if not tweets:
        return
        
    # 2. LLM analyze tweets
    analysis_result = await analyze_tweets_with_llm(tweets)
    
    # 3. Create FutureCitizen role
    role_id = await create_future_citizen_role(analysis_result)
    
    # 4. Update user's role_id
    await update_user_role(user, role_id)

async def update_user_role_task():
    """
    Main task: Update user roles
    """
    try:
        # Load environment variables
        dotenv.load_dotenv()
        bearer_token = os.getenv('BEARER_TOKEN')

        if not bearer_token:
            logger.error("Twitter API Bearer Token is missing")
            return

        logger.info("Starting Twitter role update task")
        
        # Initialize Twitter client
        client = tweepy.Client(bearer_token=bearer_token)
        
        # Get users to update
        users_to_update = User.get_empty_ai_role_id_user_list()
        if not users_to_update:
            logger.info("No users to update")
            return
        
        logger.info(f"Found {len(users_to_update)} users to update")
        
        # Process each user
        for user in users_to_update:
            if not user.x_user_id:
                logger.warning(f"User {user.id} has no Twitter ID")
                continue
                
            try:
                await process_single_user(client, user)
            except TooManyRequests:
                logger.warning("Twitter API rate limit reached. Stopping processing until next scheduled run.")
                return
            except Exception as e:
                logger.error(f"Failed to process user {user.id}: {str(e)}")
                continue
            
    except Exception as e:
        logger.error(f"Error in update_user_role_task: {str(e)}")
        raise 