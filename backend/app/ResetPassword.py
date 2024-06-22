from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import User


class ResetPassword(APIView):
    @swagger_auto_schema(
        operation_description="Отправление кода для изменения пароля на почту, которую вы указываете в url запроса",
        manual_parameters=[
            openapi.Parameter('message', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Код для сброса пароля отправлен на вашу почту'),
        ]
    )
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        code = get_random_string(length=6)

        user.code = code
        user.save()

        send_mail(
            'Сброс пароля',
            f'Ваш код для сброса пароля: {code}',
            'fittinaddmin@yandex.ru',
            [email],
            fail_silently=False
        )

        return Response({'message': 'Код для сброса пароля отправлен на вашу почту'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Изменение пароля по почте",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Указываете code, который пришёл на почту'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Новый парооль'),
            },
        )
    )
    def post(self, request, email):

        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if user.code != code:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')

        user.set_password(new_password)
        user.save()

        user.code = ''
        user.save()

        return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)
