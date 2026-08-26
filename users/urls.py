from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import (UserCreateView, email_verification,
                         password_reset_request, password_reset_sent,
                         reset_password_confirm)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("password-reset/", password_reset_request, name="password_reset"),
    path(
        "reset-password/<str:token>/",
        reset_password_confirm,
        name="reset_password_confirm",
    ),
    path("password-reset-sent/", password_reset_sent, name="password_reset_sent"),
]
