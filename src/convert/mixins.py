import os
import mimetypes
import tempfile

import requests
import convertapi

from rest_framework import status
from rest_framework.response import Response

from config import settings
from src.convert.utils import get_next_api_key
from src.convert.models import Archive, ApiKey


class FileUploadMixin:

    def process_file(self, request, serializer_class):

        file_to = request.data['to']
        file_serializer = serializer_class(data=request.data)
        if file_serializer.is_valid():
            file = request.FILES['file']
            name = file.name
            file_url = self.convert_file(file, file_to)

            if file_url:
                if request.user.is_authenticated:
                    file_name = os.path.basename(file_url)
                    file_path = os.path.join(
                        Archive.file.field.upload_to, file_name)
                    response = requests.get(file_url)
                    if response.status_code == 200:
                        with open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb') as file:
                            file.write(response.content)

                        user = request.user
                        current_format = file.name

                        archive_instance = Archive(
                            user=user,
                            name=name.split('.')[0],
                            file=file_path,
                            file_name=file_name,
                            previous_format=name.split('.')[-1],
                            current_format=current_format.split('.')[-1],
                        )

                        archive_instance.save()

                        return Response({'file_url': file_url}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Не удалось загрузить файл'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'file_url': file_url}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Не удалось обработать файл'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def convert_file(file, file_to):
        file_mime_type, _ = mimetypes.guess_type(file.name)
        file_extension = mimetypes.guess_extension(file_mime_type)

        with tempfile.NamedTemporaryFile(dir="media/temp_file/", suffix=file_extension, delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        # api_key = get_next_api_key()
        api_key = 'k9CbBHPExDzUTjIm'

        if not api_key:
            return None

        convertapi.api_secret = api_key
        result = convertapi.convert(file_to, {'File': temp_file_path})
        file_url = result.response['Files'][0]['Url']

        # try:
        #     api_key_obj = ApiKey.objects.get(key=api_key)
        #     api_key_obj.requests_remaining -= 1
        #     api_key_obj.save()

        # except ApiKey.DoesNotExist:
        #     return None

        os.remove(temp_file_path)

        return file_url
