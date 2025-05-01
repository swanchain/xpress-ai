
from app.services.contract_service import get_total_credits
from app.models.user import User
from redis.asyncio import Redis

async def check_credits_enough(
    user: User,
    redis: Redis = None
):
    uuid = user.uuid
    free_credits = user.credit
    total_generated = user.total_generated

    addon_credits = await get_total_credits(uuid, redis)

    return addon_credits + free_credits > total_generated

