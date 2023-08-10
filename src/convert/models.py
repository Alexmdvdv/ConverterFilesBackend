from django.db import models
from config import settings
from datetime import datetime


class Archive(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=50, blank=True, verbose_name='Имя файла')
    file = models.FileField(upload_to="file/", verbose_name='Путь файла')
    file_name = models.CharField(max_length=50, blank=True, verbose_name='Идентификатор файла')
    previous_format = models.CharField(max_length=20, blank=True, verbose_name='Предыдущий формат')
    current_format = models.CharField(max_length=20, blank=True, verbose_name='Текущий формат')
    created_at = models.DateField(default=datetime.now, verbose_name='Дата создания')
    is_available = models.BooleanField(default=True, verbose_name='Доступ')

    class Meta:
        verbose_name = 'Архив'
        verbose_name_plural = 'Архив'


class ApiKey(models.Model):
    key = models.CharField(max_length=100)
    requests_remaining = models.IntegerField(default=250)

    class Meta:
        verbose_name = 'Ключи'
        verbose_name_plural = 'Ключи'
