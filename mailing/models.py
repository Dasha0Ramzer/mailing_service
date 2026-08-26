from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from config import settings


class Recipient(models.Model):
    """Хранение списка получателей рассылки"""
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    full_name = models.CharField(max_length=255, blank=True, verbose_name="Ф.И.О.")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        ordering = ["email"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Хранение тем и текстов писем"""
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["subject"]

    def __str__(self):
        return self.subject


class Campaign(models.Model):
    """Описание рассылки, включая временные окна, сообщение, список получателей, владельца и текущий статус"""
    STATUS_CREATED = "Создана"
    STATUS_RUNNING = "Запущена"
    STATUS_FINISHED = "Завершена"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    message = models.ForeignKey(Message, on_delete=models.PROTECT, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipient, related_name="campaigns", verbose_name="Получатели")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns",
                              verbose_name="Автор рассылки")

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус"
    )

    last_run_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата последней попытки")

    def clean(self):
        """Валидация временных окон"""
        now = timezone.now()
        if self.start_time and self.end_time:
            if self.start_time < now:
                raise ValidationError({"start_time": "Время начала не может быть в прошлом."})
            if self.start_time >= self.end_time:
                raise ValidationError({"start_time": "Начало должно быть строго раньше окончания."})

    def update_status(self):
        """Динамический пересчет и сохранение статуса в БД в зависимости от текущего времени"""
        now = timezone.now()
        new_status = None

        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif now <= self.end_time:
            new_status = self.STATUS_RUNNING
        else:
            new_status = self.STATUS_FINISHED

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"{self.message.subject} ({self.owner.email})"


class SendAttempt(models.Model):
    """Запись каждой попытки отправки письма"""
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="attempts"
    )
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=50,
        choices=[("Успешно", "Успешно"), ("Не успешно", "Не успешно")],
    )
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ сервера")