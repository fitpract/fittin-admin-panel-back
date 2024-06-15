from rest_framework import serializers

from .models import Category, Product, Order, OrderedProduct, User, Banner


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'surname', 'password', "is_staff"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product

        fields = ['id', 'name', 'category_id', 'price', 'count', 'rating']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order

        fields = ['id', 'user_id', 'status']


class OrderedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedProduct

        fields = ['id', 'order_id', 'product_id', 'amount']
