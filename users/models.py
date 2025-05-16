from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group


class MyUserManager(BaseUserManager):
    def create_superuser(self, username, password, department_id, email='', *args, **kwargs):
        try:
            department = Department.objects.get(pk=department_id)
        except models.Model.DoesNotExist:  # Универсальный подход
            raise ValueError(f"Department with id={department_id} does not exist.")

        user = self.model(
            username=username,
            email=email if email else "",  # Защита от None
            department=department
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Statuses(models.Model):
    name = models.CharField(max_length=255, verbose_name='Статус', default='null status')
    visible_name = models.CharField(max_length=255, verbose_name='Видимое имя', default='null status')
    next_status = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_statuses',
        verbose_name='Следующий статус'
    )
    is_final = models.BooleanField(default=False, verbose_name='Финальный статус')

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return f"{self.visible_name} (→ {self.next_status.visible_name if self.next_status else 'КОНЕЦ'})"

    def validate_no_loops(self):
        """Проверка, что статусы не зациклены."""
        visited = set()
        current = self
        while current:
            if current.id in visited:
                raise ValidationError("Нарушено правило: *зацикленные статусы*!")
            visited.add(current.id)
            current = current.next_status

    def clean(self):
        super().clean()
        self.validate_no_loops()


class PossibleActions(models.Model):
    name = models.CharField(max_length=255, verbose_name='Действие', default='null action')
    visible_name = models.CharField(max_length=255, verbose_name='Видимое имя', default='null action')

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


class CustomPermissions(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Название группы доступа')
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name='Русское название')
    statuses = models.ManyToManyField(
        Statuses, blank=True, verbose_name='Изменяемые статусы', related_name='changed_statuses')
    user_can_view = models.ManyToManyField(
        Statuses, blank=True, verbose_name='Просматриваемые статусы', related_name='view_statuses')
    possible_actions = models.ManyToManyField(PossibleActions, verbose_name='Возможные действия')
    links = models.ManyToManyField(Links, verbose_name='Доступные страницы')

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Кастомная группа'
        verbose_name_plural = 'Кастомные группы'


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
        ordering = ['name']
        verbose_name = 'Название отдела'
        verbose_name_plural = 'Названия отделов'


class User(AbstractUser):
    surname = models.CharField(max_length=255, verbose_name='Отчество')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Отдел', related_name='users')
    job_title = models.CharField(max_length=255, verbose_name='Должность', default='Не указана')
    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.PROTECT, null=True,
                                       blank=True, verbose_name='Курируемая группа', related_name='curators')
    custom_permissions = models.ForeignKey(CustomPermissions, on_delete=models.PROTECT, null=True, blank=True)

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
        ordering = ['-last_name']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class CuratorToDepartment(models.Model):
    curator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Куратор')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Курируемый отдел')

    class Meta:
        verbose_name = 'Назначение куратора'
        verbose_name_plural = 'Назначения кураторов'
        # unique_together = ('curator', 'department')

    def __str__(self):
        return f"{self.curator} -> {self.department}"


class VocationsSchedule(models.Model):
    vocation_start = models.DateField(verbose_name='Начало отпуска')
    vocation_end = models.DateField(verbose_name='Конец отпуска')
    vocation_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь в отпуске')
    deputy = models.ForeignKey(User, verbose_name='Заместитель', on_delete=models.CASCADE, related_name='deputy_user')
    group = models.ForeignKey(CustomPermissions,on_delete=models.CASCADE, verbose_name='группа заместителя')

    def clean(self):
        if self.vocation_end <= self.vocation_start:
            raise ValidationError("Дата окончания отпуска должна быть позже даты начала")