from django.contrib import admin
from django.views.static import serve
from django.urls import path, include, re_path
from .yasg import urlpatterns as doc_urls

from config import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    # re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('reports/', include('reports.urls')),

    path('api-auth/', include('rest_framework.urls')),

    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += doc_urls