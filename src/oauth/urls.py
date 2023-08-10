from django.urls import path
from src.oauth.mixins import TokenRefreshView, PasswordResetConfirmAPIView, EmailConfirmationView
from src.oauth.views import UpdateUserView, RegisterView, LoginView, PasswordResetAPIView, LogoutView

urlpatterns = [
    path('update/', UpdateUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name="token"),
    path('password/reset/', PasswordResetAPIView.as_view()),
    path('password/confirm/<str:confirmation_token>/', PasswordResetConfirmAPIView.as_view(),
         name='password_reset_confirm'),
    path('email/confirm/<str:confirmation_token>/', EmailConfirmationView.as_view(), name='email_confirm'),
]
