from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group


class MyUserManager(BaseUserManager):
    def create_superuser(self, username, password, department_id, email='', *args, **kwargs):
        if email:
            user = self.model(
                username=username, email=email, department=Department.objects.get(pk=department_id))
        else:
            user = self.model(
                username=username, department=Department.objects.get(pk=department_id))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CuratorsGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name='Курируемая группа')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Карируемая группа'
        verbose_name_plural = 'Курируемые группы'


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название отдела')
    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, null=True,
                                       verbose_name='Курируемая группа')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Название отдела'
        verbose_name_plural = 'Названия отделов'


class User(AbstractUser):
    surname = models.CharField(max_length=255, verbose_name='Отчество')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Отдел')
    job_title = models.CharField(max_length=255, verbose_name='Должность', default='Не указанна')
    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.PROTECT, null=True,
                                       blank=True, verbose_name='Курируемая группа')

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


class CuratorToDepartment(models.Model):
    curator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Куратор')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Курируемый отдел')


class Statuses(models.Model):
    status = models.CharField(max_length=255, null=True, blank=True, verbose_name='Статус')
    verbose_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Видимое имя')

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.status


class PossibleActions(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Действие')
    verbose_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Видимое имя')
    new_status = models.ForeignKey(Statuses, on_delete=models.CASCADE, verbose_name='Новый статус')
    required_status = models.ForeignKey(Statuses, on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name='Требуемый статус', related_name='required_status')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Действие'
        verbose_name_plural = 'Возможные действия'


class Links(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название ссылки')
    link = models.CharField(max_length=255, verbose_name='Ссылка на страницу')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Доступные ссылки'


class CustomGroups(Group):
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название группы')
    statuses = models.ManyToManyField(Statuses, blank=True, verbose_name='Доступные статусы')
    possible_actions = models.ManyToManyField(PossibleActions, verbose_name='Возможные действия')
    links = models.ManyToManyField(Links, verbose_name='Доступные страницы')

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Кастомная группа'
        verbose_name_plural = 'Кастомные группы'


class VocationsSchedule(models.Model):
    vocation_start = models.DateField(verbose_name='Начало отпуска')
    vocation_end = models.DateField(verbose_name='Конец отпуска')
    vocation_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь в отпуске')
    deputy = models.ForeignKey(User, verbose_name='Заместитель', on_delete=models.CASCADE, related_name='deputy_user')
    group = models.ForeignKey(CustomGroups,on_delete=models.CASCADE, verbose_name='группа заместителя')
