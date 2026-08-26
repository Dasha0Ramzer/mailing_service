from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class UserRegisterForm(UserCreationForm):
    """Форма для регистрации пользователя"""
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class PasswordResetRequestForm(forms.Form):
    """Форма для сброса пароля"""
    email = forms.EmailField(label="Email", max_length=254)
