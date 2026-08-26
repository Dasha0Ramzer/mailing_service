from django import forms

from mailing.models import Campaign, Message, Recipient


class RecipientForm(forms.ModelForm):
    """Форма для модели "Получатель рассылки" """
    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите электронную почту"}
        )
        self.fields["full_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите Ф.И.О."}
        )
        self.fields["comment"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите комментарий"}
        )


class MessageForm(forms.ModelForm):
    """Форма для модели "Сообщение для рассылки" """
    class Meta:
        model = Message
        fields = ["subject", "body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите тему письма"}
        )
        self.fields["body"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите текст письма"}
        )


class CampaignForm(forms.ModelForm):
    """Форма для модели "Рассылка" """
    class Meta:
        model = Campaign
        fields = ["start_time", "end_time", "message", "recipients"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].widget = forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "Дата начала",
            }
        )
        self.fields["end_time"].widget = forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "Дата окончания",
            }
        )
        self.fields["message"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Выберите сообщение"}
        )
        self.fields["recipients"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Выберите получателей"}
        )
