from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from showcase.models import Banner, Product
from showcase.serializers import BannerSerializer

class BannerAPIView(APIView):
    """Получение/создание баннеров"""

    permission_classes = [IsAuthenticated]

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
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_FILE,
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
                'products': openapi.Schema(type=openapi.TYPE_ARRAY,
                                           items=openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                description='Список id товаров')),
                'image': openapi.Schema(type=openapi.TYPE_FILE,
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

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class BannerAPIViewDetail(APIView):
    """Получение/изменение баннера по id"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение баннера по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id баннера'),
            openapi.Parameter('header', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Заголовок баннера'),
            openapi.Parameter('description', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Описание баннера'),
            openapi.Parameter('products', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Список id товаров'),
            openapi.Parameter('image', in_=openapi.IN_QUERY, type=openapi.TYPE_FILE,
                              description='Изображение баннера'),
        ]
    )
    def get(self, request, pk):
        try:
            banner = Banner.objects.get(pk=pk)
            serializer = BannerSerializer(banner)
            return Response(serializer.data)
        except Banner.DoesNotExist:
            return Response({'error': 'Баннер не найден'},
                            status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Изменение баннера по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'header': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Заголовок баннера'),
                'description': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='Описание баннера'),
                'products': openapi.Schema(type=openapi.TYPE_ARRAY,
                                           items=openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                description='Список id товаров')),
                'image': openapi.Schema(type=openapi.TYPE_FILE,
                                        description='Изображение баннера'),
            },
        )
    )
    def put(self, request, pk):

        try:
            banner = Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            return Response({'error': 'Баннер не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление баннера по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                     description='id банера'),
            },
        )
    )
    def delete(self, request, pk):
        try:
            banner = Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            return Response({'error': 'Баннер не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        banner.delete()
        return Response("success", status=status.HTTP_204_NO_CONTENT)
