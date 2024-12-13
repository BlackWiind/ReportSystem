from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .models import User

from .forms import RegisterUserForm
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
        return reverse_lazy('raports:list')

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