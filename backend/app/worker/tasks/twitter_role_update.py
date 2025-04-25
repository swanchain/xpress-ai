import tweepy
import dotenv
import os
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.user import User
from ....services.user_service import UserService
from tweepy.errors import TooManyRequests
import httpx

logger = logging.getLogger(__name__)

class TwitterRateLimitError(Exception):
    """Custom exception for Twitter rate limit"""
    pass

async def get_user_tweets(client: tweepy.Client, user_id: int) -> List[Dict[str, Any]]:
    """
    Get user's tweets
    """
    try:
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=10,
            tweet_fields=["created_at", "public_metrics", "text", "entities", "id", "referenced_tweets"],
            expansions=["referenced_tweets.id", "referenced_tweets.id.author_id"]
        )
        
        if not tweets.data:
            logger.info(f"No tweets found for user ID: {user_id}")
            return []
            
        return [tweet.data for tweet in tweets.data]
        
    except TooManyRequests:
        logger.warning("Twitter API rate limit reached")
        raise TwitterRateLimitError("Twitter API rate limit reached")
    except Exception as e:
        logger.error(f"Error fetching tweets for user {user_id}: {str(e)}")
        raise

async def analyze_tweets_with_llm(tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Call LLM to analyze user's tweets
    """
    # TODO: Implement LLM call logic
    try:
        # TODO: Add the logic to call LLM API
        pass
    except Exception as e:
        logger.error(f"Error analyzing tweets with LLM: {str(e)}")
        raise

async def create_future_citizen_role(user_data: Dict[str, Any]) -> str:
    """
    Call FutureCitizen API to create role
    """
    try:
        # TODO: Implement the logic to call FutureCitizen API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "YOUR_FUTURECITIZEN_API_ENDPOINT",
                json=user_data,
                headers={
                    "Authorization": f"Bearer {os.getenv('FUTURECITIZEN_API_KEY')}"
                }
            )
            response.raise_for_status()
            return response.json()["role_id"]
    except Exception as e:
        logger.error(f"Error creating FutureCitizen role: {str(e)}")
        raise

async def process_single_user(client: tweepy.Client, user: User, user_service: UserService) -> None:
    """
    Process the complete process for a single user
    """
    try:
        # 1. Get user's tweets
        tweets = await get_user_tweets(client, user.x_user_id)
        if not tweets:
            return
            
        # 2. LLM analyze tweets
        analysis_result = await analyze_tweets_with_llm(tweets)
        
        # 3. Create FutureCitizen role
        role_id = await create_future_citizen_role(analysis_result)
        
        # 4. Update user's role_id
        await user_service.update_user_role_by_user_id(user.id, role_id)
        logger.info(f"Successfully processed tweets for user ID: {user.x_user_id}")
        
    except TwitterRateLimitError:
        # Pass through rate limit error
        raise
    except Exception as e:
        logger.error(f"Error processing user {user.id}: {str(e)}")
        return

async def update_user_role_task(db: AsyncSession):
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
        
        # Initialize Twitter client and user service
        client = tweepy.Client(bearer_token=bearer_token)
        user_service = UserService(db)
        
        # Get users to update
        users_to_update = await user_service.get_empty_ai_role_id_user_list()
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
                await process_single_user(client, user, user_service)
            except TwitterRateLimitError:
                logger.warning("Twitter API rate limit reached. Stopping processing until next scheduled run.")
                return
            except Exception as e:
                logger.error(f"Failed to process user {user.id}: {str(e)}")
                continue
            
    except Exception as e:
        logger.error(f"Error in update_user_role_task: {str(e)}")
        raise 