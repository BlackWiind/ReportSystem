from django.urls import path
from . import views

app_name = 'raports'

urlpatterns = [
    path('home/', views.temp_view, name='home'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('create_raport/', views.RaportCreateView.as_view(), name='create_raport'),
    path('list/', views.RaportListView.as_view(), name='list'),
    path('details/<int:pk>/', views.RaportDetailView.as_view(), name='details'),
]
