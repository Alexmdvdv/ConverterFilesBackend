from rest_framework import serializers
from src.convert.models import Archive


class FilePostAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = ('user', 'file_path')


class FilePostUnauthSerializer(serializers.Serializer):
    file_path = serializers.FileField()
    to = serializers.CharField(max_length=50)


class FileGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = ("__all__",)
