from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def create_superuser(self, username, department, password, email=None):
        if email:
            user = self.model(
                username=username, email=email, department=Department.objects.get(pk=department))
        else:
            user = self.model(
                username=username, department=Department.objects.get(pk=department))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название отдела')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Название отдела'
        verbose_name_plural = 'Названия отделов'


class User(AbstractUser):
    surname = models.CharField(max_length=255, verbose_name='Отчество')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Отдел')

    custom_objects = MyUserManager()

    REQUIRED_FIELDS = ["department"]

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.surname}'

    def __init__(self, *args, **kwargs):
        self._meta.get_field('username').verbose_name = 'Логин'
        self._meta.get_field('last_name').verbose_name = 'Фамилия'
        self._meta.get_field('first_name').verbose_name = 'Имя'
        super(User, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

# class CuratorToDepartment(models.Model):
#     curator = models.ForeignKey(User, 'Куратор')
#     department = models.ForeignKey(Department, 'Курируемый отдел')
