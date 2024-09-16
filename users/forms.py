from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class RegisterUserForm(UserCreationForm):
    groups = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Группа')

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'surname', 'department', 'job_title', ]

        def clean_username(self):
            if User.objects.filter(username__iexact=self.cleaned_data['username']):
                raise ValidationError(_("Такой логин уже существует."), code='invalid')
            return self.cleaned_data['username']

        def clean_password2(self):
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise ValidationError(_("Пароли не совпадают."), code='invalid')
            return self.cleaned_data['password2']

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
