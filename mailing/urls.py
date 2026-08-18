from django.urls import path

from mailing.views import (CampaignCreateView, CampaignDeleteView,
                           CampaignDetailView, CampaignListView,
                           CampaignRunView, CampaignUpdateView,
                           MessageCreateView, MessageDeleteView,
                           MessageDetailView, MessageListView,
                           MessageUpdateView, RecipientCreateView,
                           RecipientDeleteView, RecipientDetailView,
                           RecipientListView, RecipientUpdateView,
                           dashboard_view)

app_name = "mailing"

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    # Клиенты
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/<int:pk>/detail/",
        RecipientDetailView.as_view(),
        name="recipient_detail",
    ),
    path(
        "recipients/<int:pk>/edit/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipients/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/detail/", MessageDetailView.as_view(), name="message_detail"
    ),
    path("messages/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_update"),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    # Рассылки
    path("campaigns/", CampaignListView.as_view(), name="campaign_list"),
    path("campaigns/create/", CampaignCreateView.as_view(), name="campaign_create"),
    path(
        "campaigns/<int:pk>/detail/",
        CampaignDetailView.as_view(),
        name="campaign_detail",
    ),
    path(
        "campaigns/<int:pk>/edit/", CampaignUpdateView.as_view(), name="campaign_update"
    ),
    path(
        "campaigns/<int:pk>/delete/",
        CampaignDeleteView.as_view(),
        name="campaign_delete",
    ),
    path("campaigns/<int:pk>/run/", CampaignRunView.as_view(), name="campaign_run"),
]
