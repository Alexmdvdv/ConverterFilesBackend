import requests

from django.urls import reverse
from config import settings
from rest_framework_simplejwt.tokens import RefreshToken

from src.oauth.models import User
from src.oauth.serializers import UserSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def get_info_ip(request):
    """
    Не работает с локальным ip!!,
    поэтому нужно использовать
    любой рандомный ip адрес,
    например "170.187.137.206"
    """
    user_ip = request.META.get('HTTP_X_FORWARDED_FOR', None) or request.META.get('REMOTE_ADDR', None)

    if user_ip:
        user_ip = user_ip.split(',')[0].strip()

    return "170.187.137.206"


def get_info_user(ip):
    request = requests.get(url=f"http://ip-api.com/json/{ip}").json()
    data = {
        "user_info": {
            "country": request.get('country'),
            "city": request.get('city'),
            "timezone": request.get('timezone')
        }
    }
    return data


def get_token(user):
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    refresh_token.verify()
    user_dto = UserSerializer(user).data
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_dto": user_dto,
    }
    return data


def send_registration_confirmation_email(to_email, confirmation_token):
    subject = 'Подтверждение регистрации'

    confirmation_link = reverse('email_confirm', args=[confirmation_token])

    email_template = 'registration_confirm.html'
    context = {'confirmation_link': confirmation_link}
    html_message = render_to_string(email_template, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_message),
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send()

    try:
        user = User.objects.get(email=to_email)
        user.confirmation_token = confirmation_token
        user.save()
    except User.DoesNotExist:
        print(f"Пользователь с email '{to_email}' не найден")
