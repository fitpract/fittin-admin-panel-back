from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from app.models import Order, OrderedProduct
from app.serializers import OrderSerializer, OrderedProductSerializer

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
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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
            return Response({'error': 'Заказ не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Изменение заказа по id",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id заказа'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          description='id пользователя'),
                'status': openapi.Schema(type=openapi.TYPE_STRING,
                                         description='Статус заказа'),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER,
                                        description='Общая стоимость заказа'),
            },
        )
    )
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'},
                            status=status.HTTP_404_NOT_FOUND)

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
            return Response({'error': 'Заказ не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех заказов пользователя",
        manual_parameters=[
            openapi.Parameter('user', in_=openapi.IN_PATH, type=openapi.TYPE_INTEGER,
                              description='id пользователя'),
        ]
    )
    def get(self, request, fk):
        try:
            orders = Order.objects.filter(user=fk)
        except Order.DoesNotExist:
            return Response({'error': 'Заказы пользователя не найдены'},
                            status=status.HTTP_404_NOT_FOUND)

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