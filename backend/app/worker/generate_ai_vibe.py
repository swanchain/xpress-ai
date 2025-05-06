import logging
from typing import List, Optional
from tweepy.errors import TooManyRequests

from app.models.user import User
from app.services.user_service import UserService
from app.services.api_service import send_role_to_future_citizen
from app.services.x_service import (
    get_user_tweets_history
)
from app.services.llm_service import (
    request_llm
)
from app.services.prompt_service import (
    create_prompt_for_user_role_data,
    create_future_citizen_role_input
)
from app.database.session import get_all_objects_by_filter, AsyncSessionLocal

logger = logging.getLogger()


async def update_user_ai_role():
    """
    Update user's role_id
    """
    try:
        async with AsyncSessionLocal() as session:
            users_to_update: List[User] = await get_all_objects_by_filter(session, User, ai_role_id=None)
            
            for user in users_to_update:
                try:
                    x_user_name = user.x_screen_name
                    x_user_id = user.x_user_id
                    max_history_count = 10
                    
                    user_tweets = await get_user_tweets_history(
                        x_user_id=x_user_id,
                        x_user_name=x_user_name,
                        max_history_count=max_history_count
                    )
                
                    prompt = create_prompt_for_user_role_data(
                        tweets=user_tweets
                    )

                    role_data = await request_llm(prompt)

                    future_citizen_role_input = create_future_citizen_role_input(
                        user_role_data=role_data,
                        x_user_id=user.x_user_id,
                        x_user_name=x_user_name,
                    )

                    ai_role_id = await send_role_to_future_citizen(
                        payload=future_citizen_role_input
                    )

                    user.ai_role_id = ai_role_id
                    session.add(user)
                    await session.commit()

                except TooManyRequests:
                    logger.error("Twitter API rate limit exceeded")
                    break
                except Exception as e:
                    logger.error(f"Error processing user {user.x_screen_name}: {str(e)}")
                    continue

    except Exception as e:
        logger.error(f"Error in update_user_role_task: {str(e)}")
        raise

    