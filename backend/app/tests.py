from django.test import TestCase
from .serializers import UserSerializer
import json


class RegistrationTest(TestCase):
    def test_register(self):
        json_body = {
            'email':'user@mail.ru',
            'name':'username',
            'surname':'usersurname',
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
            'surname':'usersurname',
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
            'surname':'usersurname',
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


class AuthUserTest(TestCase):
    def setUp(self):
        json_user_body = {
            'email':'user@mail.ru',
            'name':'username',
            'surname':'usersurname',
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

    def test_user(self):
        response = self.client.get('/user/')
        self.assertEqual(response.status_code,200)


class CategoryTest(TestCase):
    def setUp(self):
        json_user_body = {
            'email':'user@mail.ru',
            'name':'username',
            'surname':'usersurname',
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
    
    def test_category_post(self):
        #post
        json_category = {
            'name':'hat',
        }
        response = self.client.post('/category/',
                        json.dumps(json_category),
                        content_type="application/json")
        self.assertEqual(response.status_code,201)
        #get
        response = self.client.get('/category/')
        print(response.data)
        self.assertEqual(response.status_code,200)
        #put
        json_category = {
            'name':'boots',
        }
        response = self.client.put('/category/1/')
        self.assertEqual(response.status_code,200)
        #delete
        response = self.client.delete('/category/1/')
        self.assertEqual(response.status_code,204)


