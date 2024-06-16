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
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.views import RegistrationAPIView, LoginAPIView, CategoryAPIView, UsersAPIView, \
    LogoutAPIView, \
    UserAPIView, CategoryDetailAPIView, ProductDetailAPIView, BannerAPIView, BannerDetailAPIView, \
    ProductAPIView

from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view()),
    path('user/', UserAPIView.as_view()),
    path('users/', UsersAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('product/', ProductAPIView.as_view()),
    path('product/<int:pk>/', ProductDetailAPIView.as_view()),
    path('category/', CategoryAPIView.as_view()),
    path('category/<int:pk>/', CategoryDetailAPIView.as_view()),
    path('banner/', BannerAPIView.as_view()),
    path('banner/<int:pk>/', BannerDetailAPIView.as_view()),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += doc_urls