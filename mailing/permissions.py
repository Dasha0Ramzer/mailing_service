from django.contrib.auth.models import User

def can_access_campaign(user: User, campaign) -> bool:
    if user.is_staff:
        return True
    return campaign.owner_id == user.id