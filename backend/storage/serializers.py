from storage.models import Storage, ProductStorage
from rest_framework import serializers


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage

        fields = '__all__'


class ProductStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStorage

        fields = '__all__'
