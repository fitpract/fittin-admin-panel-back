from django.test import TestCase
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from user.serializers import UserSerializer
from django.apps import apps
import os


class ProductTest(TestCase):
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

    def test_product(self):
        image_ = open(os.path.join(apps.get_app_config('catalog').path,'tests/1.jpg'), 'rb').read()
        image = SimpleUploadedFile(name= 'product.jpg',
                                   content= image_,
                                   content_type='image/jpeg')
            
        json_category = {
        'name':'hat',
        }
        response = self.client.post('/category/',
                    json.dumps(json_category),
                    content_type="application/json")

        form = {
            'name':'helmet',
            'category':1,
            'brand':'gucci',
            'image':image
        }

        response = self.client.post('/product/',
                    data=form)
        print(response.data)
        self.assertEqual(response.status_code,201)