from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    # path('', views.login_user, name='login'),
]
