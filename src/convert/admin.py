from django.contrib import admin
from src.convert.models import Archive, ApiKey


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "file_name",
                    "previous_format", "current_format", "created_at", "is_available"
                    )


@admin.register(ApiKey)
class ApiKey(admin.ModelAdmin):
    list_display = ("key", "requests_remaining")

