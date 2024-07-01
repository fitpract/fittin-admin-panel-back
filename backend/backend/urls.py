"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from authorization.views import RegistrationAPIView, LoginAPIView, LogoutAPIView, ResetPassword, CodeVerification
from catalog.views import ProductAPIView, ProductListAPIView, ProductAPIViewDetail, CategoryAPIView
from catalog.views import  CategoryAPIViewDetail, CategoryAPIViewByParent

from showcase.views import BannerAPIView, BannerAPIViewDetail
from storage.views import StorageAPIView, StorageAPIViewDetail, ProductStorageAPIView, ProductStorageAPIViewDetail
from storage.views import ProductStorageAPIViewByStorage

from user.views import UsersAPIView, UserAPIView
from order.views import OrderAPIView, OrderAPIViewDetail, OrdersUserAPIView
from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('registration/', RegistrationAPIView.as_view()),
    path('user/', UserAPIView.as_view()),
    path('users/', UsersAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('product/', ProductAPIView.as_view()),
    path('productList/', ProductListAPIView.as_view()),
    path('product/<int:pk>/', ProductAPIViewDetail.as_view()),
    path('category/', CategoryAPIView.as_view()),
    path('category/<int:pk>/', CategoryAPIViewDetail.as_view()),
    path('categoryByParent/<int:pk>/', CategoryAPIViewByParent.as_view()),
    path('banner/', BannerAPIView.as_view()),
    path('banner/<int:pk>/', BannerAPIViewDetail.as_view()),
    path('order/', OrderAPIView.as_view()),
    path('order/<int:pk>/', OrderAPIViewDetail.as_view()),
    path('ordersUser/<int:fk>/', OrdersUserAPIView.as_view()),
    path('storage/', StorageAPIView.as_view()),
    path('storage/<int:pk>', StorageAPIViewDetail.as_view()),
    path('productStorage/', ProductStorageAPIView.as_view()),
    path('productStorage/<int:pk>/', ProductStorageAPIViewDetail.as_view()),
    path('productStorageByStorage/<int:fk>/', ProductStorageAPIViewByStorage.as_view()),
    path('codeVerification/<str:email>/', CodeVerification.as_view()),
    path('resetPassword/<str:email>/', ResetPassword.as_view()),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += doc_urls
