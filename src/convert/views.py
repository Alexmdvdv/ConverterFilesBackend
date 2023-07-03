import os
from config.settings import MEDIA_ROOT

from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse

from src.convert.mixins import FileUploadMixin
from src.convert.models import Archive
from src.convert.serializers import FilePostAuthSerializer, FilePostUnauthSerializer, FileGetSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated


class FileUploadView(APIView, FileUploadMixin):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.permission_classes = [IsAuthenticated]
            return self.process_file(request, FilePostAuthSerializer)
        else:
            return self.process_file(request, FilePostUnauthSerializer)

    def get(self, request, *args, **kwargs):
        user = request.user
        archives = Archive.objects.filter(user=user)

        serializer = FileGetSerializer(archives, many=True)

        return JsonResponse(serializer.data, safe=False)


class FileDownloadView(View):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        try:
            file_field = Archive.objects.get(
                id=file_id).file_path
            file_path = default_storage.path(file_field.name)

            with open(file_path, 'rb') as file:
                file_data = file.read()

            response = HttpResponse(file_data, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + file_field.name
            return response
        except Exception as e:
            return HttpResponse('Ошибка при скачивании файла: {}'.format(str(e)))


class FileDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Archive.objects.all()

    def delete(self, request, pk):
        try:
            instance = Archive.objects.get(pk=pk)
            file_path = os.path.join(MEDIA_ROOT, instance.file_path.path)

            if os.path.exists(file_path):
                os.remove(file_path)

            instance.delete()
            return Response("Файл успешно удален", status=status.HTTP_204_NO_CONTENT)
        except Archive.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
