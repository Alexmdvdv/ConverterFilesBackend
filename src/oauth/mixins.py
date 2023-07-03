from config import settings


class TokenCookieMixin:
    @staticmethod
    def set_token_cookie(response, refresh_token):
        response.set_cookie(
            key='token',
            value=str(refresh_token),
            httponly=True,
            secure=settings.CSRF_COOKIE_SECURE,
        )
