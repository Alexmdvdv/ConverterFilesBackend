from config import settings
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from src.oauth.utils import get_token
from src.oauth.models import User
from src.oauth.serializers import (
    PasswordResetConfirmSerializer, UserSerializer)


class TokenCookieMixin:
    @staticmethod
    def set_token_cookie(response, refresh_token):
        response.set_cookie(
            key='token',
            value=str(refresh_token),
            httponly=True,
            secure=settings.CSRF_COOKIE_SECURE,
        )


class EmailConfirmationView(TokenCookieMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, confirmation_token):
        user = get_object_or_404(User, confirmation_token=confirmation_token)

        user.is_confirmed = True
        user.save()

        token = get_token(user)

        response = Response(
            {"access_token": str(token.get("access_token")),
             'user': token.get("user_dto")},
            status=status.HTTP_201_CREATED
        )

        self.set_token_cookie(response, token.get("refresh_token"))

        return response


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, confirmation_token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(password_reset_token=confirmation_token)

        except User.DoesNotExist:
            return Response({'detail': 'Недействительный токен'},
                            status=status.HTTP_400_BAD_REQUEST)

        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.password_reset_token = None
        user.save()

        return Response({'detail': 'Пароль был сброшен'}, status=status.HTTP_200_OK)


class TokenRefreshView(TokenCookieMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.COOKIES.get('token')

        if not token:
            return Response({'error': 'Refresh token не предоставлен'}, status=400)

        try:
            refresh_token = RefreshToken(token)
            access_token = refresh_token.access_token
            refresh_token.verify()

            user = JWTAuthentication().get_user(access_token)
            user_dto = UserSerializer(user).data

            response = Response(
                {"access_token": str(access_token), 'user': user_dto},
                status=status.HTTP_201_CREATED
            )
            self.set_token_cookie(response, refresh_token)
            return response

        except InvalidToken:
            return Response({'error': 'Недействительный refresh token'}, status=400)

        except TokenError:
            return Response({'error': 'Ошибка при обработке токена'}, status=400)
