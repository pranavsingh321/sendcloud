from django.conf import settings
from django.core.mail import send_mail


def send_feed_failure_email(
    user_email: str, message: str, subject: str
) -> None:
    # send the email to the recipent
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
    )
