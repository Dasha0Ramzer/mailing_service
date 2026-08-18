from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from .models import Campaign, SendAttempt


def send_campaign(campaign_id: int) -> dict:
    """Запуск рассылки"""
    from_email = EMAIL_HOST_USER
    campaign = Campaign.objects.get(pk=campaign_id)
    now = timezone.now()

    if not (campaign.start_time <= now <= campaign.end_time):
        SendAttempt.objects.create(
            campaign=campaign,
            sent_at=now,
            status="Не успешно",
            server_response="Время вне окна отправки",
        )
        return {"success": False, "error": "Время вне окна", "total": 0, "success_count": 0, "fail_count": 1}

    recipients = list(campaign.recipients.all())
    total = len(recipients)

    if total == 0:
        return {"success": False, "error": "Нет получателей", "total": 0, "success_count": 0, "fail_count": 0}

    attempts_to_save = []
    success_count = 0
    fail_count = 0

    for recipient in recipients:
        try:
            send_mail(
                subject=campaign.message.subject,
                message=campaign.message.body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            status = "Успешно"
            server_response = "OK"
            success_count += 1
        except Exception as e:
            status = "Не успешно"
            server_response = str(e)[:255]
            fail_count += 1

        attempts_to_save.append(
            SendAttempt(
                campaign=campaign,
                recipient=recipient,
                sent_at=now,
                status=status,
                server_response=server_response,
            )
        )

    SendAttempt.objects.bulk_create(attempts_to_save)

    campaign.last_run_at = now
    campaign.save(update_fields=['last_run_at'])

    return {
        "success": True,
        "total": total,
        "success_count": success_count,
        "fail_count": fail_count,
    }
