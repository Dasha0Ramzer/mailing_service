from django.contrib import admin

from users.models import User
from .models import Campaign, Message, Recipient, SendAttempt


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Отображение модели "Получатель рассылки" в админке"""
    list_display = ("full_name", "email")
    search_fields = ("full_name", "email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Отображение модели "Сообщение для рассылки" в админке"""
    list_display = ("subject",)
    search_fields = ("subject",)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Отображение модели "Рассылка" в админке"""
    list_display = ("id", "status", "start_time", "end_time")
    filter_horizontal = ("recipients",)


@admin.register(SendAttempt)
class SendAttemptAdmin(admin.ModelAdmin):
    """Отображение модели "Попытка рассылки" в админке"""
    list_display = ("campaign", "recipient", "status", "sent_at")
    list_filter = ("status",)
