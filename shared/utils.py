
from django.core.mail import send_mail
from django.conf import settings

def send_to_mail(email, message):

    send_mail(
        subject="Ro'yxatdan o'tishni tasdiqlash kodi",
        message=f"Tasdiqlash kodingiz: {message}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )