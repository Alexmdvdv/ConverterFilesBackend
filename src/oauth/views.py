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
from datetime import timedelta

from src.oauth.mixins import TokenCookieMixin
from src.oauth.models import User
from src.oauth.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserUpdateSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class RegisterView(TokenCookieMixin, APIView):
    """{
    "user": {"username": "..",
    "email": "..",
    "password": ".."}
    }"""
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user', {})
        serializer = UserRegistrationSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        refresh_token.verify()

        response = Response({"access_token": str(access_token)}, status=status.HTTP_201_CREATED)
        self.set_token_cookie(response, refresh_token)

        return response


class LoginView(TokenCookieMixin, APIView):
    """{
        "user": {"username": "..",
        "password": ".."}
        }"""
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user', {})
        serializer = UserLoginSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        refresh_token.verify()

        response = Response({"access_token": str(access_token)}, status=status.HTTP_201_CREATED)
        self.set_token_cookie(response, refresh_token)

        return response


class UpdateUserView(APIView):
    """{
        "user": {
        "username": "..",
        "email": "..",
        }
        }"""
    permission_classes = [IsAuthenticated]

    @staticmethod
    def patch(request):
        user_data = request.data.get('user', {})
        user = request.user

        serializer = UserUpdateSerializer(user, data=user_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenRefreshView(TokenCookieMixin, APIView):
    """
    Cookie: {token="refresh_token"},
    Authorization: {Bearer "acces_token"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.COOKIES.get('token')

        if not token:
            return Response({'error': 'Refresh token не предоставлен'}, status=400)

        try:
            refresh_token = RefreshToken(token)
            access_token = refresh_token.access_token
            refresh_token.verify()

            response = Response({"access_token": str(access_token)}, status=200)
            self.set_token_cookie(response, refresh_token)
            return response

        except InvalidToken:
            return Response({'error': 'Недействительный refresh token'}, status=400)

        except TokenError:
            return Response({'error': 'Ошибка при обработке токена'}, status=400)


class PasswordResetAPIView(APIView):
    """{
    "email": ".."
    }"""
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

            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_url = request.build_absolute_uri(reset_url)

            user.password_reset_token = timezone.localtime()
            print(timezone.localtime())
            user.save()

            subject = 'Запрос на сброс пароля'
            message = f'Пожалуйста, нажмите на ссылку ниже, чтобы сбросить пароль:\n\n{reset_url}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return Response({'detail': 'Email для сброса пароля был отправлен'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    """{
        "new_password": "..",
        "confirm_password": ".."
    }"""
    permission_classes = [AllowAny]

    @staticmethod
    def post(request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = int(uidb64)
                user = User.objects.get(pk=uid)
            except (ValueError, User.DoesNotExist):
                return Response({'detail': 'Недействительный пользователь или токен'},
                                status=status.HTTP_400_BAD_REQUEST)

            if default_token_generator.check_token(user, token):
                token_created = user.password_reset_token
                time_difference = timezone.localtime() - token_created
                expiration_time = timedelta(hours=1)

                if time_difference <= expiration_time:
                    new_password = serializer.validated_data.get('new_password')
                    user.set_password(new_password)
                    user.save()

                    return Response({'detail': 'Пароль был сброшен'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Ссылка для сброса пароля истекла'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'Недействительный пользователь или токен'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
