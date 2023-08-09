import uuid

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from src.oauth.models import User
from src.oauth.mixins import TokenCookieMixin
from src.oauth.utils import get_info_user, get_info_ip, get_token, \
    send_registration_confirmation_email
from src.oauth.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserUpdateSerializer,
    PasswordResetSerializer)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_data = request.data.get('user', {})
        user_info = get_info_user(get_info_ip(request)).get('user_info')

        serializer = UserRegistrationSerializer(
            data={**user_data, **user_info})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_token = str(uuid.uuid4())

        data = {
            "email": user.email,
            "subject": 'Завершите регистрацию на eelisey.store',
            "confirmation_token": confirmation_token,
            "email_template": "registration_confirm.html",
            "link": "email_confirm",
            "field": "confirmation_token"
        }

        send_registration_confirmation_email(data)

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
            {"access_token": str(token.get("access_token")),
             'user': token.get("user_dto")},
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

        response = Response(
            {'detail': 'Вы успешно вышли из системы'}, status=status.HTTP_200_OK)
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

            confirmation_token = str(uuid.uuid4())

            data = {
                "email": email,
                "subject": 'Подтверждение сброса пароля',
                "confirmation_token": confirmation_token,
                "email_template": "password_reset_confirm.html",
                "link": "password_reset_confirm",
                "field": "password_reset_token"
            }
            send_registration_confirmation_email(data)

            return Response(
                {"message": f"Сообщение со сбросом пароля отправлено на вашу почту {email}"},
                status=status.HTTP_200_OK)
