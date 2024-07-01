from rest_framework import serializers

from generate_desc.generate_description import generate_product_description
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product

        fields = '__all__'

    def save(self, **kwargs):
        description = self.validated_data.get('description', None)
        name = self.validated_data.get('name', None)
        if not description and name:
            self.validated_data['description'] = generate_product_description(name)
        return super().save(**kwargs)
