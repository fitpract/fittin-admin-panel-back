import datetime

import jwt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User, Product, Order, OrderedProduct, Category

from app.serializers import UserSerializer, ProductSerializer, CategorySerializer, OrderSerializer, \
    OrderedProductSerializer


class UsersAPIView(APIView):
    """Вывод списка пользователей"""

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class RegistrationAPIView(APIView):
    """Регистрация. Обязательные поля email, name, password"""

    def post(self, request):
        email = request.data.get('email')

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Пользователь с этим email уже зарегистрирован.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    """Вход по полям email и password"""

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('Неправильный email или пароль')
        if not user.check_password(password):
            raise AuthenticationFailed('Неправильный email или пароль')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response


class UserAPIView(APIView):
    """Получение залогининого пользователя"""

    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutAPIView(APIView):
    """Выход из аккаунта"""

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')

        response.data = {
            'message': 'success'
        }
        return response


class ProductAPIView(APIView):
    """get и post запросы для"""

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            new_category = serializer.save()

            parent_name = request.data.get('parent')
            if parent_name:
                try:
                    parent_category = Category.objects.get(name=parent_name)
                    parent_category.child = f"{parent_category.child}, {new_category.name}" if parent_category.child else new_category.name
                    parent_category.save()
                except Category.DoesNotExist:
                    return Response({'error': 'Parent category not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        def delete_descendants(category):
            for child_name in category.child:
                try:
                    child_category = Category.objects.get(name=child_name)
                    delete_descendants(child_category)
                    child_category.delete()
                except Category.DoesNotExist:
                    pass

        delete_descendants(category)
        category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'])
    def order_by_user(self, request):
        # Получаем идентификатор пользователя из запроса
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(data={'error': 'User ID обязателен в параметрах запроса'},
                            status=status.HTTP_400_BAD_REQUEST)

        orders = Order.object.filter(user_id=user_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def product_in_order(self, request):
        order_id = request.query_params.get('order_id')
        product_id = request.query_params.get('product_id')
        if not order_id or not product_id:
            return Response(data={'error': 'Order ID и Product ID обязательны в параметрах запроса'},
                            status=status.HTTP_400_BAD_REQUEST)

        product_in_order = OrderedProduct.objects.filter(order_id=order_id, product_id=product_id).first()
        if not product_in_order:
            return Response(data={'error': 'Продукт не найден в указанном заказе'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = OrderedProductSerializer(product_in_order)
        return Response(serializer.data)
