from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth.tokens import default_token_generator

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from src.oauth.utils import TokenCookieMixin
from src.oauth.models import User
from src.oauth.serializers import (PasswordResetConfirmSerializer, UserSerializer)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class EmailConfirmationView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, confirmation_token):
        user = get_object_or_404(User, confirmation_token=confirmation_token)

        user.is_confirmed = True
        user.save()

        return Response({"message": "Email успешно подтвержден"}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
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
                    new_password = serializer.validated_data.get(
                        'new_password')
                    user.set_password(new_password)
                    user.save()

                    return Response({'detail': 'Пароль был сброшен'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Ссылка для сброса пароля истекла'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'Недействительный пользователь или токен'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
