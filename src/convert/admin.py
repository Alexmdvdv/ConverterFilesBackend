from django.contrib import admin
from src.convert.models import Archive


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ("user", "file_path", "file_name",
                    "previous_format", "current_format", "created_at", "is_available"
                    )
