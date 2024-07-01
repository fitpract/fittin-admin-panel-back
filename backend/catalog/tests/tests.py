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
        response = self.client.post('/login/', json.dumps(json_login_body), content_type="application/json")
        cookies = response.cookies.get('jwt').value
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + cookies

    def test_product(self):
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
            'image':image,
            'description':'descr'
        }
        response = self.client.post('/product/', data=form)
        product_id = response.data['id']
        self.assertEqual(response.status_code,201)
        print('product post done')

        #get
        response = self.client.get('/product/')
        self.assertEqual(response.status_code,200)
        print('product get done')
        
        #get detail
        response = self.client.get('/product/{0}/'.format(product_id))
        self.assertEqual(response.status_code,200)
        print('product detail get done')

        #put
        put_json = {
            'name':'boots',
            'description':'descri'

        }
        response = self.client.put('/product/{0}/'.format(product_id), put_json,
                                   content_type="application/json")
        self.assertEqual(response.status_code,200)
        print('product put done')

        #delete
        response = self.client.delete('/product/{0}/'.format(product_id))
        self.assertEqual(response.status_code,204)
        print('product delete done')


class CategorytTest(TestCase):
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
    
    def test_category(self):
        #post
        json_category = {
            'id':2,
            'name':'jeans',
        }
        response = self.client.post('/category/',
                        json.dumps(json_category),
                        content_type="application/json")
        category_id = response.data['id']
        self.assertEqual(response.status_code,201)
        print('category post done')

        #get
        response = self.client.get('/category/')
        self.assertEqual(response.status_code,200)

        print('category get done')

        #get detail
        response = self.client.get('/category/{0}/'.format(category_id))
        self.assertEqual(response.status_code,200)
        print('category detail get done')

        #put
        json_category = {
            'name':'boots',
        }
        response = self.client.put('/category/{0}/'.format(category_id))
        self.assertEqual(response.status_code,200)
        print('category put done')

        #delete
        response = self.client.delete('/category/{0}/'.format(category_id))
        self.assertEqual(response.status_code,204)
        print('category delete done')
