import uuid

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from src.oauth.mixins import TokenCookieMixin
from src.oauth.utils import get_info_user, get_info_ip, get_token, \
    send_registration_confirmation_email
from src.oauth.models import User
from src.oauth.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserUpdateSerializer,
    PasswordResetSerializer)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user', {})
        user_info = get_info_user(get_info_ip(request)).get('user_info')

        serializer = UserRegistrationSerializer(data={**user_data, **user_info})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_token = str(uuid.uuid4())
        send_registration_confirmation_email(user.email, confirmation_token)

        return Response({"message": f"Сообщение с подтверждением отправлено на вашу почту {user_data.get('email')}"},
                        status=status.HTTP_200_OK)


class LoginView(TokenCookieMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user', {})
        serializer = UserLoginSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        if not user.is_confirmed:
            return Response({"message": "Email пользователя не подтвержден"}, status=status.HTTP_403_FORBIDDEN)

        token = get_token(user)

        response = Response(
            {"access_token": str(token.get("access_token")), 'user': token.get("user_dto")},
            status=status.HTTP_201_CREATED
        )
        self.set_token_cookie(response, token.get("refresh_token"))

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        refresh_token = request.COOKIES.get('token')

        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = Response({'detail': 'Вы успешно вышли из системы'}, status=status.HTTP_200_OK)
        response.delete_cookie('token')

        return response


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def patch(request):
        user_data = request.data.get('user', {})
        user = request.user

        serializer = UserUpdateSerializer(user, data=user_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'Пользователь с указанным адресом электронной почты не существует'},
                                status=status.HTTP_400_BAD_REQUEST)

            token = default_token_generator.make_token(user)
            uid = user.pk

            reset_url = reverse('password_reset_confirm', kwargs={
                'uidb64': uid, 'token': token})
            reset_url = request.build_absolute_uri(reset_url)

            user.password_reset_token = timezone.localtime()
            user.save()

            subject = 'Запрос на сброс пароля'
            message = f'Пожалуйста, нажмите на ссылку ниже, чтобы сбросить пароль:\n\n{reset_url}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return Response({'detail': 'Email для сброса пароля был отправлен'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
