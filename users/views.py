import secrets

from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from config.settings import EMAIL_HOST_USER
from users.forms import PasswordResetRequestForm, UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "register.html"
    success_url = "/users/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Регистрация"
        return context

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()

            if user:
                token = secrets.token_hex(16)
                user.token = token
                user.save()

                host = request.get_host()
                reset_link = f"http://{host}/users/reset-password/{token}/"

                subject = "Сброс пароля"
                message = (
                    f"Здравствуйте!\n\n"
                    f"Вы запросили сброс пароля. Нажмите на ссылку ниже, чтобы установить новый пароль:\n"
                    f"{reset_link}\n\n"
                    f"Если вы не запрашивали сброс, просто проигнорируйте это письмо."
                )

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[email],
                )

                messages.success(request, "Инструкция отправлена на почту")
                return redirect("users:password_reset_sent")
            else:
                messages.success(request, "Пользователь с таким email не существует")
                return redirect("users:login")
    else:
        form = PasswordResetRequestForm()

    return render(request, "password_reset_request.html", {"form": form})


def reset_password_confirm(request, token):
    user = get_object_or_404(User, token=token)

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.token = None
            user.save()
            messages.success(request, "Пароль успешно сброшен. Теперь вы можете войти.")
            return redirect("users:login")
    else:
        form = SetPasswordForm(user)

    return render(request, "reset_password_form.html", {"form": form, "token": token})


def password_reset_sent(request):
    return render(request, "password_reset_sent.html")
