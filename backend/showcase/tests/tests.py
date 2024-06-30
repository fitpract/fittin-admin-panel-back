from django.test import TestCase
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from user.serializers import UserSerializer
from django.apps import apps
import os

class BannerTest(TestCase):
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

    def test_banner(self):
        #post
        image_ = open(os.path.join(apps.get_app_config('catalog').path,'tests/1.jpg'), 'rb').read()
        image = SimpleUploadedFile(name= 'product.jpg', content= image_, content_type='image/jpeg') 
        json_category = {
        'name':'hat'
        }
        response= self.client.post('/category/', data=json_category, content_type="application/json")
        category_id = response.data['id']
        form = {
            'name':'helmet',
            'category':category_id,
            'brand':'gucci',
            'description':'descr'
        }
        response = self.client.post('/product/', data=form)
        product_id = response.data['id']

        form = {
            'header':'sail',
            'products':product_id,
            'description':'descr',
            'image':image
        }
        response = self.client.post('/banner/', data=form)
        self.assertEqual(response.status_code,201)
        banner_id = response.data['id']

        #get
        response = self.client.get('/banner/')
        self.assertEqual(response.status_code,200)
        print('banner get done')

        #get detail
        response = self.client.get('/banner/{0}/'.format(banner_id))
        self.assertEqual(response.status_code,200)
        print('banner detail get done')

        #put
        put_json = {
            'name':'boots',
            'description':'descri'

        }
        response = self.client.put('/banner/{0}/'.format(banner_id), put_json,
                                   content_type="application/json")
        self.assertEqual(response.status_code,200)
        print('banner put done')

        #delete
        response = self.client.delete('/banner/{0}/'.format(banner_id))
        self.assertEqual(response.status_code,204)
        print('banner delete done')
