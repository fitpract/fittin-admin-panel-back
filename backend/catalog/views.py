from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from catalog.models import Product, Category
from catalog.serializers import ProductSerializer, CategorySerializer
from generate_desc import generate_description


class ProductAPIView(APIView):
    """Получение/создание товаров"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех товаров",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id товара'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название товара'),
            openapi.Parameter('description', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Описание товара'),
            openapi.Parameter('brand', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название бренда товара'),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории к которой относится товар'),
            openapi.Parameter('price', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Цена товара'),
            openapi.Parameter('count', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество товара'),
            openapi.Parameter('rating', in_=openapi.IN_QUERY, type=openapi.FORMAT_FLOAT,
                              description='Рейтинг товара'),
            openapi.Parameter('sorder_order', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Позиция товара в списке'),
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_FILE,
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
                'description': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Описание товара (необязательное поле)'),
                'brand': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Название бренда товара (необязательное поле)'),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER,
                                           description='id категории к которой относится товар (необязательное поле)'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Цена товара (по умолчанию 1)'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Количество товара (по умолчанию 0)'),
                'rating': openapi.Schema(type=openapi.FORMAT_FLOAT,
                                         description='Рейтинг товара (по умолчанию 5)'),
                'sorder_order': openapi.Schema(type=openapi.TYPE_INTEGER,
                                               description='Позиция товара в списке (по умолчанию 1)'),
                'image': openapi.Schema(type=openapi.TYPE_FILE,
                                        description='Изображение товара (по умолчанию null)'),

            },
        )
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class ProductAPIViewDetail(APIView):
    """Получение/изменение товара по id"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение товара по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id товара'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название товара'),
            openapi.Parameter('description', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Описание товара'),
            openapi.Parameter('brand', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название бренда товара'),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории к которой относится товар'),
            openapi.Parameter('price', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Цена товара'),
            openapi.Parameter('count', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Количество товара'),
            openapi.Parameter('rating', in_=openapi.IN_QUERY, type=openapi.FORMAT_FLOAT,
                              description='Рейтинг товара'),
            openapi.Parameter('sorder_order', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Позиция товара в списке'),
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_FILE,
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
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название товара (обязательное поле)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Описание товара (необязательное поле)'),
                'brand': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Название бренда товара (необязательное поле)'),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER,
                                           description='id категории к которой относится товар (необязательное поле)'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Цена товара (по умолчанию 1)'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Количество товара (по умолчанию 0)'),
                'rating': openapi.Schema(type=openapi.FORMAT_FLOAT,
                                         description='Рейтинг товара (по умолчанию 5)'),
                'sorder_order': openapi.Schema(type=openapi.TYPE_INTEGER,
                                               description='Позиция товара в списке (по умолчанию 1)'),
                'image': openapi.Schema(type=openapi.TYPE_FILE,
                                        description='Изображение товара (по умолчанию null)'),

            },
        )
    )
    def put(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'},
                            status=status.HTTP_404_NOT_FOUND)

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
                'id': openapi.Schema(type=openapi.TYPE_STRING,
                                     description='id товара'),
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Добавление списка товаров",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Название товара (обязательное поле)'),
                    'description': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description='Описание товара (необязательное поле)'),
                    'brand': openapi.Schema(type=openapi.TYPE_STRING,
                                            description='Название бренда товара (необязательное поле)'),
                    'category': openapi.Schema(type=openapi.TYPE_INTEGER,
                                               description='id категории к которой относится товар (необязательное поле)'),
                    'price': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='Цена товара (по умолчанию 1)'),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='Количество товара (по умолчанию 0)'),
                    'rating': openapi.Schema(type=openapi.FORMAT_FLOAT,
                                             description='Рейтинг товара (по умолчанию 5)'),
                    'sorder_order': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                   description='Позиция товара в списке (по умолчанию 1)'),
                    'image': openapi.Schema(type=openapi.TYPE_FILE,
                                            description='Изображение товара (по умолчанию null)'),

                },
            )
        )
    )
    def post(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Данные должны быть в виде списка"},
                            status=status.HTTP_400_BAD_REQUEST)

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
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название категории'),
            openapi.Parameter('parent_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id родительской категории'),
            openapi.Parameter('sorder_order', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Позиция категории в списке'),
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_FILE,
                              description='Изображение категории'),
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
                                       description='Название категории(можно изменить'),
                'parent_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='id родительской категории'),
                'sorder_order': openapi.Schema(type=openapi.TYPE_INTEGER,
                                               description='Позиция категории в списке'),
                'image': openapi.Schema(type=openapi.TYPE_FILE,
                                        description='Изображение категории'),
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
                    return Response({'error': 'Родительская категория не найдена'},
                                    status=status.HTTP_404_NOT_FOUND)

            new_category = serializer.save(parent=parent_category)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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
            openapi.Parameter('parent_id', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='id родительской категории'),
            openapi.Parameter('sorder_order', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Позиция категории в списке'),

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
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название категории(можно изменить'),
                'parent_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description='id родительской категории'),
                'sorder_order': openapi.Schema(type=openapi.TYPE_INTEGER,
                                               description='Позиция категории в списке'),
                'image': openapi.Schema(type=openapi.TYPE_FILE,
                                        description='Изображение категории'),
            },
        )
    )
    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Категория не найдена'},
                            status=status.HTTP_404_NOT_FOUND)

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
                    return Response({'error': 'id родительской категории не найдено'},
                                    status=status.HTTP_404_NOT_FOUND)
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


class CategoryAPIViewByParent(APIView):
    """Получение количества под категорий"""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение категории по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id категории'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название категории'),
            openapi.Parameter('parent_id', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='id родительской категории'),
            openapi.Parameter('sorder_order', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Позиция категории в списке'),

        ]
    )
    def get(self, request, pk):
        try:
            parent_category = Category.objects.get(pk=pk)
            child_categories = Category.objects.filter(parent=parent_category)
            return Response({'count': child_categories.count()})

        except Category.DoesNotExist:
            return Response({'error': 'The category with the specified ID was not found'}, status=404)
