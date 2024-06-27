from rest_framework import serializers
from .models import Order, OrderedProduct

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order

        fields = '__all__'


class OrderedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedProduct

        fields = '__all__'