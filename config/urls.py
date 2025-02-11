from django.contrib import admin
from django.views.static import serve
from django.urls import path, include, re_path
from .yasg import urlpatterns as doc_urls

from config import settings

urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('home/', include('reports.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

urlpatterns += doc_urls