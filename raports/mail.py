from django.core.mail import send_mail
from config.settings import EMAIL_RECIPIENTS, EMAIL_HOST_USER


def send_email(text, sender):
    send_mail(
        "Система рапортов, обратная связь",
        f"{text}\n\nОтправитель:{sender}",
        EMAIL_HOST_USER,
        EMAIL_RECIPIENTS,
        fail_silently=False,
    )
