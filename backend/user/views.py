from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from app.models import User
from app.serializers import UserSerializer

class UserAPIView(APIView):
    """Получение авторизованного пользователя"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение данных авторизованного пользователя (все параметры, кроме пароля) ",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id пользователя'),
            openapi.Parameter('email', in_=openapi.IN_QUERY, type=openapi.FORMAT_EMAIL,
                              description='Почта пользователя'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Имя пользователя'),
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
    

class UsersAPIView(APIView):
    """Вывод списка пользователей"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получение всех пользователей",
        manual_parameters=[
            openapi.Parameter('id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='id пользователя'),
            openapi.Parameter('email', in_=openapi.IN_QUERY, type=openapi.FORMAT_EMAIL,
                              description='Почта пользователя'),
            openapi.Parameter('name', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Имя пользователя'),
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