from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from mailing.forms import CampaignForm, MessageForm, RecipientForm
from mailing.models import Campaign, Message, Recipient, SendAttempt
from mailing.services import send_campaign


# --- Получатели рассылки (Recipient) ---
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "recipient_list.html"
    context_object_name = "recipient_list"

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(campaigns__owner=self.request.user).distinct()
        return qs


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "recipient_form.html"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("recipient_list")
    template_name = "recipient_delete.html"


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "recipient_detail.html"
    context_object_name = "recipient_detail"


# --- Сообщения (Message) ---
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "message_list.html"
    context_object_name = "message_list"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "message_form.html"
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:message_list")
    template_name = "message_delete.html"


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "message_detail.html"
    context_object_name = "message_detail"


# --- Рассылки (Campaign) ---
class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = "campaign_list.html"
    context_object_name = "campaign_list"

    def get_queryset(self):
        qs = Campaign.objects.select_related("message").prefetch_related("recipients")

        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)

        return qs


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "campaign_form.html"
    success_url = reverse_lazy("mailing:campaign_list")

    def form_valid(self, form):
        campaign = form.save(commit=False)
        campaign.owner = self.request.user
        campaign.save()
        form.save_m2m()
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "campaign_form.html"
    success_url = reverse_lazy("mailing:campaign_list")

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        return qs


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    success_url = reverse_lazy("mailing:campaign_list")
    template_name = "campaign_delete.html"
    context_object_name = "campaign_detail"

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        return qs


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "campaign_detail.html"
    context_object_name = "campaign_detail"

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        return qs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class CampaignRunView(LoginRequiredMixin, View):
    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        return render(request, "campaign_run.html", {"campaign": campaign})

    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        result = send_campaign(campaign.id)

        if result["success"]:
            messages.success(
                request,
                f"Рассылка запущена. Всего писем: {result['total']}, "
                f"успешно: {result['success_count']}, ошибок: {result['fail_count']}",
            )
        else:
            error_text = result.get("error", "Не удалось запустить рассылку.")
            messages.error(request, error_text)

        return redirect(reverse_lazy("mailing:campaign_list"))


@cache_page(60 * 5)
def home(request):
    now = timezone.now()

    total_campaigns = Campaign.objects.count()
    active_campaigns = Campaign.objects.filter(
        start_time__lte=now, end_time__gte=now
    ).count()
    unique_recipients = Recipient.objects.count()

    context = {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "unique_recipients": unique_recipients,
    }
    return render(request, "home.html", context)


@login_required
def dashboard_view(request):
    user = request.user
    is_manager = user.is_staff

    qs_campaigns = Campaign.objects.all()
    if not is_manager:
        qs_campaigns = qs_campaigns.filter(owner=user)

    if qs_campaigns.count() == 0:
        context = {
            "is_manager": is_manager,
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "total_messages_sent": 0,
        }
        return render(request, "dashboard.html", context)

    stats = SendAttempt.objects.filter(
        campaign__in=qs_campaigns
    ).aggregate(
        total_attempts=Count("id"),
        successful_attempts=Count("id", filter=Q(status="Успешно")),
        failed_attempts=Count("id", filter=Q(status="Не успешно")),
        total_messages_sent=Count("id", filter=Q(status="Успешно")),
    )

    context = {
        "is_manager": is_manager,
        "total_attempts": stats["total_attempts"] or 0,
        "successful_attempts": stats["successful_attempts"] or 0,
        "failed_attempts": stats["failed_attempts"] or 0,
        "total_messages_sent": stats["total_messages_sent"] or 0,
    }

    return render(request, "dashboard.html", context)
