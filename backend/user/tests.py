from django.test import TestCase
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from user.serializers import UserSerializer
from django.apps import apps
import os


class UserTest(TestCase):
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
        response = self.client.post('/login/', json.dumps(json_login_body), content_type="application/json")
        cookies = response.cookies.get('jwt').value
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + cookies

    def test_user(self):
        #get list
        response = self.client.get('/users/')
        self.assertEqual(response.status_code,200)

        #get detail
        response = self.client.get('/user/')
        self.assertEqual(response.status_code,200)