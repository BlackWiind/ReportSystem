from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('get_users/', views.get_all_users, name='get_users'),
    path('usernames_loader/', views.SearchUser.as_view(), name='usernames_loader'),
    path('new_vocation/', views.NewVocation.as_view(), name='new_vocation'),

    path('api/list_curator_group/', views.ListCuratorsGroup.as_view(), name='list_curator_group'),
    path('api/list_users/', views.GetUsers.as_view(), name='list_users'),
    path('api/my_department_list_users/', views.GetUsersFromMyDepartment.as_view(), name='my_department_list_users'),
    path('api/user_data/<int:pk>/', views.GetOneUser.as_view(), name='user_data'),
]
