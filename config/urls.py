from django.contrib import admin
from django.urls import include, path

from mailing.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("mailing/", include("mailing.urls", namespace="mailing")),
    path("users/", include("users.urls", namespace="users")),
]
