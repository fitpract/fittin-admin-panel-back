from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string


from app.models import User
from app.serializers import UserSerializer


class RegistrationAPIView(APIView):
    """Регистрация нового пользователя"""

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.FORMAT_EMAIL,
                                        description='Email пользователя (обязательное поле)'),
                'name': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Имя пользователя (обязательное поле)'),
                'surname': openapi.Schema(type=openapi.TYPE_STRING,
                                          description='Фамилия пользователя'),
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
                'email': openapi.Schema(type=openapi.TYPE_STRING,
                                        description='Email пользователя'),
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
            return Response({'error': 'Пользователь не найден'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Неправильный пароль'},
                            status=status.HTTP_401_UNAUTHORIZED)

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
    

class CodeVerification(APIView):
    @swagger_auto_schema(
        operation_description="Отправление кода для изменения пароля на почту, которую вы указываете в url запроса",
        manual_parameters=[
            openapi.Parameter('message', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description=
                              'Код для сброса пароля отправлен на вашу почту. Он действителен в течение 30 минут'),
        ]
    )
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        code = get_random_string(length=6)

        user.code = code
        user.code_expiration_time = timezone.now() + timezone.timedelta(minutes=30)
        user.save()

        send_mail(
            'Сброс пароля',
            f'Ваш код для сброса пароля: {code}. Он действителен в течение 30 минут.',
            'fittinaddmin@yandex.ru',
            [email],
            fail_silently=False
        )

        return Response(
            {'message': 'Код для сброса пароля отправлен на вашу почту. Он действителен в течение 30 минут'},
            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Проверка кода, который был отправлен на почту",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING,
                                       description='Указываете code, который пришёл на почту'),
            },
        )
    )
    def post(self, request, email):
        code = request.data.get('code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if 'true_change' == user.code:
            return Response({'message': 'Код уже прошёл проверку'}, status=status.HTTP_200_OK)

        if user.code_expiration_time < timezone.now():
            user.code = ''
            user.save()
            return Response({'error': 'Срок действия кода истек'}, status=status.HTTP_400_BAD_REQUEST)

        if user.code != code:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

        user.code = 'true_change'
        user.save()
        return Response({'message': 'Код прошёл проверку'}, status=status.HTTP_200_OK)


class ResetPassword(APIView):
    @swagger_auto_schema(
        operation_description="Проверка кода, который был отправлен на почту",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_password': openapi.Schema(type=openapi.TYPE_STRING,
                                               description='Новый пароль'),
            },
        )
    )
    def post(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if not (user.code == 'true_change'):
            return Response({'error': 'Код не был подтвержден'}, status=status.HTTP_400_BAD_REQUEST)

        if user.code_expiration_time < timezone.now():
            user.code = ''
            user.code_expiration_time = None
            user.save()
            return Response({'error': 'Срок действия кода истек'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')

        user.set_password(new_password)
        user.save()

        user.code = ''
        user.code_expiration_time = None
        user.save()

        return Response({'message': 'Ваш пароль успешно изменён'}, status=status.HTTP_200_OK)