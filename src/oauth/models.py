from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Имя пользователя должно быть заполнено")
        if not email:
            raise ValueError("Поле \"Электронная почта\" должно быть заполнено")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True, verbose_name="Имя")
    email = models.EmailField(db_index=True, unique=True, verbose_name="Email")
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    timezone = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateField(default=datetime.now)
    updated_at = models.DateField(default=datetime.now)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    confirmation_token = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'


