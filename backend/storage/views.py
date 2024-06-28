from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from catalog.models import Product
from storage.models import Storage, ProductStorage
from storage.serializers import StorageSerializer, ProductStorageSerializer

from rest_framework.response import Response


class StorageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех складов",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id склада'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название склада'),
            openapi.Parameter('location', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Адрес склада'),
            openapi.Parameter('coordinates', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Координаты склада'),
        ]
    )
    def get(self, request):
        """
        Получение всех складов
        """
        storages = Storage.objects.all()
        serializer = StorageSerializer(storages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Создание нового склада",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название склада'),
                'location': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Адрес склада'),
                'coordinates': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Координаты склада'),

            },
        )
    )
    def post(self, request):
        """
        Создание нового склада
        """
        serializer = StorageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StorageAPIViewDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех складов по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id пользователя'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Название склада'),
            openapi.Parameter('location', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Адрес склада'),
            openapi.Parameter('coordinates', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Координаты склада'),
        ]
    )
    def get(self, request, pk):
        """
            Получение склада по ID
        """
        try:
            storage = Storage.objects.get(pk=pk)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = StorageSerializer(storage)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Изменение склада по id в url",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Название склада'),
                'location': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='Адрес склада'),
                'coordinates': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Координаты склада'),

            },
        )
    )
    def put(self, request, pk):
        """
            Изменение склада по ID
        """
        try:
            storage = Storage.objects.get(pk=pk)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = StorageSerializer(storage, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
            Удаление склада по ID
        """
        try:
            storage = Storage.objects.get(pk=pk)
        except Storage.DoesNotExist:
            return Response({'error': 'Склад не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        storage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductStorageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение информации о товарах на складе",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id product_storage модели'),
            openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id товара'),
            openapi.Parameter('storage', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id склада'),
            openapi.Parameter('count_product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Количество товара'),

        ]
    )
    def get(self, request):
        """
        Получение информации о товарах на складе
        """

        products = ProductStorage.objects.all()

        serializer = ProductStorageSerializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Создание новой записи о товаре на складе",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'storage': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          description='id склада'),
                'product': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          description='id товара'),
                'count_product': openapi.Schema(type=openapi.TYPE_STRING,
                                                description='Количество товара'),
            },
        )
    )
    def post(self, request):
        """
        Создание новой записи о товаре на складе
        """
        storage_id = request.data.get('storage')
        product_id = request.data.get('product')

        storage = Storage.objects.get(pk=storage_id)
        product = Product.objects.get(pk=product_id)

        product_storage = ProductStorage.objects.create(
            storage=storage,
            product=product,
            count_product=request.data.get('count_product', 0)
        )

        serializer = ProductStorageSerializer(product_storage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductStorageAPIViewDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение информации о товарах на складе по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id product_storage модели'),
            openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id товара'),
            openapi.Parameter('storage', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id склада'),
            openapi.Parameter('count_product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Количество товара'),

        ]
    )
    def get(self, request, pk):
        """
            Получение информации о товаре на складе по id в url
        """
        try:
            product_storage = ProductStorage.objects.get(pk=pk)
            serializer = ProductStorageSerializer(product_storage)
            return Response(serializer.data)
        except ProductStorage.DoesNotExist:
            return Response({'error': 'Product storage не найден'},
                            status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Измение информации о товаре на складе по id в url",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'storage': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          description='id склада'),
                'product': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          description='id товара'),
                'count_product': openapi.Schema(type=openapi.TYPE_STRING,
                                                description='Количество товара'),
            },
        )
    )
    def put(self, request, pk):
        """
            Измение информации о товаре на складе по id
        """
        try:
            productStorage = ProductStorage.objects.get(pk=pk)
        except ProductStorage.DoesNotExist:
            return Response({'error': 'Товар на складе не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ProductStorageSerializer(productStorage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление информации о товаре на складе по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id product_storage'),
        ]
    )
    def delete(self, request, pk):
        try:
            product_storage = ProductStorage.objects.get(pk=pk)
        except ProductStorage.DoesNotExist:
            return Response({'error': 'Модель ProductStorage не найдена'}, status=status.HTTP_404_NOT_FOUND)

        product_storage.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)


class ProductStorageAPIViewByStorage(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех складов с товарами по id склада",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id product_storage модели'),
            openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id товара'),
            openapi.Parameter('storage', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id склада'),
            openapi.Parameter('count_product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Количество товара'),

        ]
    )
    def get(self, request, fk):
        """
        Получение всех складов с товарами по id склада
        """
        try:
            products = ProductStorage.objects.filter(storage_id=fk)
            serializer = ProductStorageSerializer(products, many=True)
            return Response(serializer.data)
        except ProductStorage.DoesNotExist:
            return Response({"detail": "Склад не найден"}, status=status.HTTP_404_NOT_FOUND)
