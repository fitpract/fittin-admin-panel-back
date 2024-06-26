from django.urls import path
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Django админ панель",
        default_version='v1',
        description="Базовые запросы для админ панели",
        license=openapi.License(name="BSD License"),
    ),
    url='https://fittinadminpanel.ru',
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
<<<<<<< HEAD
=======
    #path('swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
>>>>>>> dev
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
