from django.db import models
from config import settings


class Archive(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    file_path = models.FileField(upload_to="file/", verbose_name='Путь файла')
    file_name = models.CharField(max_length=20, blank=True, verbose_name='Имя файла')
    previous_format = models.CharField(max_length=20, blank=True, verbose_name='Предыдущий формат')
    current_format = models.CharField(max_length=20, blank=True, verbose_name='Текущий формат')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_available = models.BooleanField(default=True, verbose_name='Доступ')

    class Meta:
        verbose_name = 'Архив'
        verbose_name_plural = 'Архив'
