from django.urls import path
from . import views

app_name = 'raports'

urlpatterns = [
    path('home/', views.temp_view, name='home'),
]
