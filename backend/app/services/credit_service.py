
from app.services.contract_service import get_total_credits
from app.models.user import User

def check_credits_enough(
    user: User
):
    uuid = user.uuid
    free_credits = user.credit
    total_generated = user.total_generated

    addon_credits = get_total_credits(uuid)

    return addon_credits + free_credits > total_generated

