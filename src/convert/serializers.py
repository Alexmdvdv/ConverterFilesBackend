from rest_framework import serializers
from src.convert.models import Archive


class FilePostAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = ['file']


class FilePostUnauthSerializer(serializers.Serializer):
    file = serializers.FileField()
    to = serializers.CharField(max_length=50)


class FileGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = "__all__"
