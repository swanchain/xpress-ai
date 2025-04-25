from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.database.session import get_all_objects_by_filter
from app.services.api_service import get_futurecitizen_bearer_token_async
import tweepy
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Add mock tweets for testing
class MockTweet:
    """Mock Tweet class for testing"""
    def __init__(self, text, created_at=None):
        self.text = text
        self.created_at = created_at

MOCK_TWEETS_DATA = [
    MockTweet("@MarioNawfal $1.5B spent every year!? Wow, that makes my political contributions last year small by comparison."),
    MockTweet("RT @_jaybaxter_: The reason posts with links sometimes get lower reach is not because they are explicitly downranked by any evil rule or lo…"),
    MockTweet("@SERobinsonJr @_jaybaxter_ That does need some love"),
    MockTweet("@SawyerMerritt Uh oh 😬 Inverse Cramer is tough karma to overcome!"),
    MockTweet("I'm calling weekend reviews with Autopilot to accelerate progress."),
    MockTweet("@nataliegwinters 💯"),
    MockTweet("RT @SawyerMerritt: NEWS: Tesla reportedly has 300 test operators driving around Austin, Texas to prepare for their big June robotaxi launch…"),
    MockTweet("@SawyerMerritt Waymo needs \"way mo\" money to succeed 😂"),
    MockTweet("@MarioNawfal Cool"),
    MockTweet("Good move. There are thousands of committees that take up a lot of time without clear accomplishments. A reset was needed."),
    MockTweet("To be clear, there is no explicit rule limiting the reach of links in posts. The algorithm tries (not always successfully) to maximize user-seconds on 𝕏, so a link that causes people to cut short their time here will naturally get less exposure.")
]
class UserService:
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_list(self) -> List[User]:
        """Get all users"""
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_x_user_id(self, x_user_id: int) -> Optional[User]:
        """Get user by Twitter user ID"""
        result = await self.db.execute(select(User).filter(User.x_user_id == x_user_id))
        return result.scalar_one_or_none()

    async def get_empty_ai_role_id_user_list(self) -> List[User]:
        """Get all users with empty AI role ID"""
        return await get_all_objects_by_filter(self.db, User, ai_role_id=None)

    async def get_user_by_wallet_address(self, wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        result = await self.db.execute(select(User).filter(User.wallet_address == wallet_address))
        return result.scalar_one_or_none()

    async def update_user_role_by_user_id(self, user_id: int, role_id: str) -> None:
        """Update user's AI role ID"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(ai_role_id=role_id)
        )
        await self.db.commit()

    async def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Update user data"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
        )
        await self.db.commit()
        return await self.get_user_by_id(user_id)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False 
    
    async def get_user_tweets(self, client: tweepy.Client, user_id: int, max_results: int = 10, use_mock: bool = False) -> Optional[List[tweepy.Tweet]]:
        """
        Get user's tweets
        Args:
            client: Tweepy client instance
            user_id: Twitter user ID
            use_mock: Whether to use mock data (for testing)
        Returns:
            Optional[List[tweepy.Tweet]]: List of tweets or None if no tweets found
        """
        if use_mock:
            return MOCK_TWEETS_DATA

        tweets = client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            tweet_fields=["created_at", "public_metrics", "text", "entities", "id", "referenced_tweets"],
            expansions=["referenced_tweets.id", "referenced_tweets.id.author_id"]
        )
        
        if not tweets.data:
            return None
            
        return tweets.data
    
    async def get_user_role_details(self, user_id: int) -> Optional[dict]:
        """Get user's role details"""
        user = await self.get_user_by_id(user_id)
        if not user or not user.ai_role_id:
            return None
            
        try:
            # Get bearer token
            bearer_token = await get_futurecitizen_bearer_token_async()
            
            # Make API call to get role details
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    os.environ['FUTURECITIZEN_GET_USER_ROLE_DETAIL'] + f"/{user.ai_role_id}",
                    headers={
                        "accept": "application/json",
                        "Authorization": f"Bearer {bearer_token}"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get role details: {response.text}")
                    return None
                    
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting role details: {str(e)}")
            return None
            
            