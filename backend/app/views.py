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

from app.models import User, Product, Order, OrderedProduct, Category, Banner

from app.serializers import UserSerializer, ProductSerializer, BannerSerializer, OrderSerializer, \
    OrderedProductSerializer, CategorySerializer


class UsersAPIView(APIView):
    """Вывод списка пользователей"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех пользователей",
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
    """Регистрация нового пользователя"""

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
            response.set_cookie(key='jwt', value=str(token['access']), httponly=True)
            return response

        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class UserAPIView(APIView):
    """Получение авторизованного пользователя"""
    permission_classes = [IsAuthenticated]

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
        user_id = request.user.id

        user = User.objects.filter(id=user_id).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutAPIView(APIView):
    """Выход из аккаунта, нет полей"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')

        response.data = {
            'message': 'success'
        }
        return response


class ProductAPIView(APIView):
    """Получение/создание товаров"""
    permission_classes = [IsAuthenticated]

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
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Изображение товара'),

        ]
    )
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Создание нового товара",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название товара (обязательное поле)'),
                'category_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                              description='id категории к которой относится товар (обязательное поле)'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Цена товара (обязательное поле)'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Количество товара (по умолчанию 0)'),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER,
                                         description='Рейтинг товара (по умолчанию 5)'),
                'image': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Изображение товара (по умолчанию null)'),

            },
        )
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductAPIViewDetail(APIView):
    """Получение/изменение товара по id"""
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
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Изображение товара'),

        ]
    )
    def get(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Изменение товара по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название товара'),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='id категории'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Цена товара'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара'),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Рейтинг товара'),
                'image': openapi.Schema(type=openapi.TYPE_STRING, description='Изображение товара'),
            },
        )
    )
    def put(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление товара по id",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='id товара'),
            },
        )
    )
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден.'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)


class ProductListAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Добавление списка товаров",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Название товара (обязательное поле)'),
                    'category_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                  description='id категории к которой относится '
                                                              'товар (обязательное поле)'),
                    'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Цена товара'),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='Количество товара (по умолчанию 0)'),
                    'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Рейтинг товара (по умолчанию 5)'),
                },
            )
        )
    )
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Данные должны быть в виде списка"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryAPIView(APIView):
    """Получение/создание категорий"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех категорий",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id категории'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название категории'),
            openapi.Parameter('parent_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id родительской категории'),
        ]
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Добавление новой категории",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название категории (обязательное поле)'),
                'parent_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='id родительской категории (необязательное поле)'),
            },
        )
    )
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            parent_id = request.data.get('parent_id')
            parent_category = None
            if parent_id:
                try:
                    parent_category = Category.objects.get(pk=parent_id)
                except Category.DoesNotExist:
                    return Response({'error': 'Родительская категория не найдена'}, status=status.HTTP_404_NOT_FOUND)

            new_category = serializer.save(parent=parent_category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryAPIViewDetail(APIView):
    """Получение/изменение категории по id"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение категории по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название категории'),
            openapi.Parameter('parent', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='id родительской категории'),

        ]
    )
    def get(self, request, pk):

        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Изменение категории по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название категории(можно изменить'),
                'parent_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='id родительской категории'),
            },
        )
    )
    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            new_parent_id = request.data.get('parent_id')
            if new_parent_id is not None:
                try:
                    new_parent_category = Category.objects.get(pk=new_parent_id)
                    category.parent = new_parent_category
                    category.save()
                except Category.DoesNotExist:
                    return Response({'error': 'id родительской категории не найдено'}, status=status.HTTP_404_NOT_FOUND)
            else:
                category.parent = None
                category.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление категории по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории'),
        ]
    )
    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)


class BannerAPIView(APIView):
    """Получение/создание баннеров"""

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех баннеров",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id баннера'),
            openapi.Parameter('header', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Заголовок баннера'),
            openapi.Parameter('description', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Описание баннера'),
            openapi.Parameter('products', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Список id товаров'),
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Изображение баннера'),

        ]
    )
    def get(self, request):
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Создание нового баннера",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'header': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Заголовок баннера (обязательное поле)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Описание баннера (по умолчанию пустое поле)'),
                'products': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                         description='Список id товаров')),
                'image': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Изображение баннера (по умолчанию null) ')
            },
        )
    )
    def post(self, request):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            products_ids = request.data.get('products')
            if products_ids:
                products = Product.objects.filter(pk__in=products_ids)
                serializer.instance.products.set(products)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BannerAPIViewDetail(APIView):
    """Получение/изменение баннера по id"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение баннера по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='id баннера'),
            openapi.Parameter('header', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Заголовок баннера'),
            openapi.Parameter('description', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Описание баннера'),
            openapi.Parameter('products', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Список id товаров'),
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Изображение баннера'),
        ]
    )
    def get(self, request, pk):
        try:
            banner = Banner.objects.get(pk=pk)
            serializer = BannerSerializer(banner)
            return Response(serializer.data)
        except Banner.DoesNotExist:
            return Response({'error': 'Баннер не найден'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Изменение баннера по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'header': openapi.Schema(type=openapi.TYPE_STRING, description='Заголовок баннера'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание баннера'),
                'products': openapi.Schema(type=openapi.TYPE_INTEGER, description='Список id товаров'),
                'image': openapi.Schema(type=openapi.TYPE_STRING, description='Изображение баннера'),
            },
        )
    )
    def put(self, request, pk):

        try:
            banner = Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            return Response({'error': 'Баннер не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление баннера по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id банера'),
            },
        )
    )
    def delete(self, request, pk):
        try:
            banner = Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            return Response({'error': 'Баннер не найден'}, status=status.HTTP_404_NOT_FOUND)

        banner.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех заказов",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
            openapi.Parameter('user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id пользователя'),
            openapi.Parameter('status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Статус заказа'),
            openapi.Parameter('price', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Общая стоимость заказа'),
        ]
    )
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Создание нового заказа",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       description='id пользователя (обязательное поле)'),
                'status': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Статус заказа (по умолчанию "formed")'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Общая стоимость заказа (обязательное поле)'),
            },
        )
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderAPIViewDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение заказа по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
            openapi.Parameter('user', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id пользователя'),
            openapi.Parameter('price', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='Общая цена заказа'),
            openapi.Parameter('status', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='Статус заказа'),
        ]
    )
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Изменение заказа по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id пользователя'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Статус заказа'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description='Общая стоимость заказа'),
            },
        )
    )
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление заказа по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id заказа'),
        ]
    )
    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех заказов пользователя",
        manual_parameters=[
            openapi.Parameter('user', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='id пользователя'),
        ]
    )
    def get(self, request, fk):
        try:
            orders = Order.objects.filter(user=fk)
        except Order.DoesNotExist:
            return Response({'error': 'Заказы пользователя не найдены'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


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
