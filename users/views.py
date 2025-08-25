from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import generics, status, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reports.permissions import IsSuperuserOrReadOnly
from reports.utils.utils import new_vocation, LargeResultsSetPagination
from .models import User, CuratorsGroup, Department

from .forms import RegisterUserForm
from .serializers import UserSerializer, CuratorsGroupSerializer, UserShortDataSerializer, DepartmentSerializer, \
    VacationSerializer
from .utils.search_in_db import SearchUsers


class UserRegisterView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    form_class = RegisterUserForm
    success_message = 'Пользователь успешно зарегестрирован.'
    my_tags = ['Users', ]

    def form_valid(self, form):
        response = super(UserRegisterView, self).form_valid(form)
        self.object.groups.add(form.cleaned_data['groups'])
        return response

class NewVacationView(generics.CreateAPIView):
    """ Создание записи об отпуске и назначение заместителя"""
    serializer_class = VacationSerializer
    my_tags = ['Other', ]

    def perform_create(self, serializer):
        vacation_user = self.request.user
        deputy = serializer.validated_data['deputy']

        try:
            serializer.save(
                vocation_user=vacation_user,
                group=deputy.custom_permissions
            )
        except Exception as e:
            raise serializers.ValidationError("Не получилось создать запись об отпуске")

class AllUsersListView(generics.ListCreateAPIView):
    """
    Возвращает список всех пользователей,
     для редактирования доступно только суперюзеру.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    pagination_class = LargeResultsSetPagination
    my_tags = ['Users', ]

class GetUsersFromMyDepartment(generics.ListAPIView):
    serializer_class = UserSerializer
    my_tags = ['Users', ]

    def get_queryset(self):
        return User.objects.filter(department=self.request.user.department)

class ListCuratorsGroup(generics.ListAPIView):
    """Создание и список курируемых групп"""
    queryset = CuratorsGroup.objects.all()
    serializer_class = CuratorsGroupSerializer
    my_tags = ['Curators', ]

class GetOneUser(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    my_tags = ['Users', ]

class GetUserMyUserData(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    my_tags = ['Users', ]


    def get_object(self):
        obj = get_object_or_404(self.filter_queryset(self.get_queryset()), pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)

        return obj

class GetUsersForReport(generics.ListAPIView):
    """Возвращает список юзеров, которых можно назначить ответственными"""
    serializer_class = UserShortDataSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    my_tags = ['Users', ]

    def get_queryset(self):
        try:
            if self.request.user.custom_permissions.name == 'curator':
                return User.objects.filter(department__curators_group=self.request.user.curators_group)
            return User.objects.filter(department=self.request.user.department)
        except AttributeError:
            raise AttributeError('Не установлены права пользователя')

class GetAllDepartment(generics.ListAPIView):
    """Список всех департаментов"""
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    my_tags = ['Departments', ]
    queryset = Department.objects.all()