from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import RegisterUserForm


class UserRegisterView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    form_class = RegisterUserForm
    success_message = 'Пользователь успешно зарегестрирован.'
