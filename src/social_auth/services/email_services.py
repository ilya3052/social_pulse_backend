from django.core.mail import send_mail

from social_pulse import settings


def send_email(subject, message, email):
    try:
        send_mail(
            subject=subject,
            message="",
            html_message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False)
    except Exception:
        raise
