import datetime

import jwt
from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User, Product, Order, OrderedProduct, Category

from app.serializers import UserSerializer, ProductSerializer, CategorySerializer, OrderSerializer, \
    OrderedProductSerializer


class UsersAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """Вывод списка пользователей"""

    @swagger_auto_schema(
        operation_description="Получить список пользователей",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id пользователя'),
            openapi.Parameter('email', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Почта пользователя'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Имя пользователя'),
            openapi.Parameter('surname', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Фамилия пользователя'),
            openapi.Parameter('is_staff', in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Если значение True, пользователь является админом'),

        ]
    )
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class RegistrationAPIView(APIView):
    """Регистрация. Обязательные поля email, name, password"""

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя (обязательное поле)'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя (обязательное поле)'),
                'surname': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Пароль пользователя(обязательное поле)'),
                'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                           description='Если значение True, пользователь является админом'),
            },
        )
    )
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
    """Вход в аккаунт"""

    @swagger_auto_schema(
        operation_description="Авторизация пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Пароль пользователя'),
            },
        )
    )
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({'error': 'Неправильный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Неправильный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'user_id': user.id,
                'name': user.name
            })
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            response = Response(token, status=status.HTTP_200_OK)
            response.set_cookie(key='jwt', value=str(refresh), httponly=True)
            return response

        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """Получение авторизованного пользователя"""

    @swagger_auto_schema(
        operation_description="Получение данных авторизованного пользователя (все параметры, кроме пароля) ",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id пользователя'),
            openapi.Parameter('email', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Почта пользователя'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Имя пользователя'),
            openapi.Parameter('surname', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Фамилия пользователя'),
            openapi.Parameter('is_staff', in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Если значение True, пользователь является админом'),

        ]
    )
    def get(self, request):
        permission_classes = [IsAuthenticated]
        user_id = request.user.id

        user = User.objects.filter(id=user_id).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """Выход из аккаунта, нет полей"""

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')

        response.data = {
            'message': 'success'
        }
        return response


class ProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """get и post запросы для товаров"""

    @swagger_auto_schema(
        operation_description="Получение всех товаров",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id товара'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название товара'),
            openapi.Parameter('category_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории к которой относится товар'),
            openapi.Parameter('price', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Цена товара'),
            openapi.Parameter('count', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество товара'),
            openapi.Parameter('rating', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Рейтинг товара'),

        ]
    )
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Post запрос для товаров",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название товара (обязательное поле)'),
                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                              description='id категории к которой относится товар (обязательное поле)'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Цена товара (обязательное)'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара (по умолчанию 0)'),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Рейтинг товара (по умолчанию 5)'),
            },
        )
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductAPIViewId(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение товара по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id товара'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название товара'),
            openapi.Parameter('category_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории к которой относится товар'),
            openapi.Parameter('price', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Цена товара'),
            openapi.Parameter('count', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество товара'),
            openapi.Parameter('rating', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Рейтинг товара'),

        ]
    )
    def get(self, request, pk):
        """
        Получение товара по id.
        """
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Изменение товара по id",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название товара'),
                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id категории'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Цена товара'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара'),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Рейтинг товара'),
            },
        )
    )
    def put(self, request, pk):
        """
        Изменение товара по id.
        """
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """get и post запросы для категорий"""

    @swagger_auto_schema(
        operation_description="Получение всех категорий",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id категории'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название категории'),
            openapi.Parameter('parent', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Предок категории'),
            openapi.Parameter('child', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Потомоки категории'),

        ]
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Post запрос для категорий",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название категории (обязательное поле)'),
                'parent': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Предок категории (по умолчанию пустая строка)'),
                'child': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Потомоки категории (по умолчанию пусткая строка)'),
            },
        )
    )
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


class CategoryAPIViewId(APIView):
    """
    Get и post запрос для получения/изменения категории по id.
    """

    @swagger_auto_schema(
        operation_description="Получение категории по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id категории'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название категории'),
            openapi.Parameter('parent', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Предок категории'),
            openapi.Parameter('child', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Потомоки категории'),

        ]
    )
    def get(self, request, pk):

        """
        Получение категории по id.
        """
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Изменение категории по id",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название категории(можно изменить'),
                'parent': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Предок категории (можно изменить)'),
                'child': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Потомоки категории (лучше не менять)'),
            },
        )
    )
    def put(self, request, pk):
        """
        Изменение категории по id.
        """
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            previous_parent_name = category.parent

            serializer.save()

            if previous_parent_name:
                try:
                    parent_category = Category.objects.get(name=previous_parent_name)
                    parent_category.child = parent_category.child.replace(f", {category.name}", "")
                    parent_category.child = parent_category.child.strip(", ")
                    parent_category.save()
                except Category.DoesNotExist:
                    pass
            new_parent_name = request.data.get('parent')
            if new_parent_name:
                try:
                    new_parent_category = Category.objects.get(name=new_parent_name)
                    new_parent_category.child = f"{new_parent_category.child}, {category.name}" if new_parent_category.child else category.name
                    new_parent_category.save()
                except Category.DoesNotExist:
                    return Response({'error': 'Parent category not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """Удаление категории по id в url запросе"""

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
    permission_classes = [IsAuthenticated]
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
