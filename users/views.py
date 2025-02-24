from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reports.permissions import IsSuperuserOrReadOnly
from reports.utils.utils import new_vocation
from .models import User, CuratorsGroup

from .forms import RegisterUserForm
from .serializers import UserSerializer, CuratorsGroupSerializer
from .utils.search_in_db import SearchUsers


class UserRegisterView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    form_class = RegisterUserForm
    success_message = 'Пользователь успешно зарегестрирован.'

    def form_valid(self, form):
        response = super(UserRegisterView, self).form_valid(form)
        self.object.groups.add(form.cleaned_data['groups'])
        return response


class UserLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('reports:list')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный логин или пароль')
        return self.render_to_response(self.get_context_data(form=form))


class UserLogoutView(LogoutView):
    def get_success_url(self):
        return reverse_lazy('users:login')


def get_all_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        return JsonResponse(data={'users': users})


class SearchUser(View):
    def get(self, request):
        return SearchUsers(request.GET['search']).search()


class NewVocation(View):
    def post(self, request):
        # try:
        return new_vocation(request.user,
                            request.POST['deputy[]'][0],
                            request.POST['vocation_start'],
                            request.POST['vocation_end'])
        # except Exception as e:
        #     return JsonResponse(data={'message': f'Произошла неизвестная ошибка: {type(e).__name__}'}, status=500)

class GetUsers(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperuserOrReadOnly]

class GetUsersFromMyDepartment(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(department=self.request.user.department)

class ListCuratorsGroup(generics.ListAPIView):
    """Создание и список курируемых групп"""
    queryset = CuratorsGroup.objects.all()
    serializer_class = CuratorsGroupSerializer

class GetOneUser(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]