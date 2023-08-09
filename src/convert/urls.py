from django.urls import path
from src.convert.views import FileUploadView, FileDownloadView, FileDeleteView

urlpatterns = [
    path('upload/', FileUploadView.as_view()),
    path('download/<int:file_id>/', FileDownloadView.as_view()),
    path('delete/<int:pk>/', FileDeleteView.as_view())
]
