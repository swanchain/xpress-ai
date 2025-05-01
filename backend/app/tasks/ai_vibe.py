from app.celery_app import celery_app
import asyncio
import logging

from app.database.session import AsyncSessionLocal, get_one_object_by_filter
from app.services.x_service import get_user_tweets_history
from app.services.prompt_service import (
    create_prompt_for_user_role_data,
    create_future_citizen_role_input,
)
from app.services.llm_service import request_llm
from app.services.api_service import send_role_to_future_citizen
from app.models.user import User

logger = logging.getLogger()

@celery_app.task(name="refresh_user_vibe")
def refresh_user_vibe_task(user_id: int):
    asyncio.run(_refresh_user_vibe(user_id))


async def _refresh_user_vibe(user_id: int):
    async with AsyncSessionLocal() as session:
        try:
            user: User = await get_one_object_by_filter(session, User, id=user_id)
            if not user:
                logger.error(f"User {user_id} not found.")
                return

            x_user_name = user.x_screen_name
            x_user_id = user.x_user_id
            max_history_count = 10

            try:
                tweets = await get_user_tweets_history(
                    x_user_id=x_user_id,
                    x_user_name=x_user_name,
                    max_history_count=max_history_count
                )
            except Exception as e:
                logger.error(f"X API error: {str(e)}")
                return

            try:
                prompt = create_prompt_for_user_role_data(tweets=tweets)
                role_data = await request_llm(prompt)
            except Exception as e:
                logger.error(f"LLM error: {str(e)}")
                return

            try:
                role_input = create_future_citizen_role_input(
                    user_role_data=role_data,
                    x_user_id=x_user_id,
                    x_user_name=x_user_name
                )
                ai_role_id = await send_role_to_future_citizen(payload=role_input)

                user.ai_role_id = ai_role_id
                session.add(user)
                await session.commit()

            except Exception as e:
                logger.error(f"FutureCitizen error: {str(e)}")
                return

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
