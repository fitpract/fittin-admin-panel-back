from django.test import TestCase
from user.serializers import UserSerializer
import json

class RegistrationTest(TestCase):
    def test_register(self):
        json_body = {
            'email':'user@mail.ru',
            'name':'username',
            'password':'pass'
        }
        response = self.client.post('/registration/',
                                    json.dumps(json_body),
                                    content_type="application/json")
        self.assertEqual(response.status_code,200)


class LoginTest(TestCase):
    def setUp(self):
        json_body = {
            'email':'user@mail.ru',
            'name':'username',
            'password':'pass'
        }
        serializer =UserSerializer(data=json_body)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    
    def test_status_code(self):
        json_body = {
            'email':'user@mail.ru',
            'password':'pass'
        }
        response = self.client.post('/login/',
                                    json.dumps(json_body),
                                    content_type="application/json")
        self.assertEqual(response.status_code,200)


class LogoutTest(TestCase):
    def setUp(self):
        json_user_body = {
            'email':'user@mail.ru',
            'name':'username',
            'password':'pass'
        }
        serializer =UserSerializer(data=json_user_body)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        json_login_body = {
            'email':'user@mail.ru',
            'password':'pass'
        }
        response = self.client.post('/login/',
                        json.dumps(json_login_body),
                        content_type="application/json")
        cookies = response.cookies.get('jwt').value
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + cookies

    def test_logout(self):
        response = self.client.post('/logout/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.cookies.get('jwt').value,'')