from django.urls import path, include
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title="PassPort API",
        default_version='v1',
        description="PassPort API",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="License: Apache-2.0"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        path("api/v1/account/", include("account.api.v1.urls")),
        path("api/v1/services/", include("service.api.v1.urls")),
    ],
    authentication_classes=[JWTAuthentication]
)

urlpatterns = [
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='redoc'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
