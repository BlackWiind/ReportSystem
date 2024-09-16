from django.utils.timezone import now

from django.db import models

from users.models import User, CuratorsGroup


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name='Тэг')
    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, null=True,
                                       verbose_name='Курируемая группа')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Raport(models.Model):
    status_choices = (
        ('created', 'создан'),
        ('approved_by_curator', 'одобрен куратором'),
        ('approved_by_director', 'одобрен главным врачём'),
        ('in_purchasing_department', 'в отделе закупок'),
        ('rejected', 'отклонён'),
    )

    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создатель рапорта')
    text = models.TextField(verbose_name='Текст')
    justification = models.TextField(verbose_name='Основание')
    union = models.BooleanField(default=False, verbose_name='Объеденённый рапорт')
    status = models.CharField(max_length=255, choices=status_choices, default='created')
    rejection_reason = models.TextField(null=True)
    tags = models.ManyToManyField(Tag)
    price = models.FloatField(default=0.00, verbose_name='Цена')
    one_time = models.BooleanField(default=True, verbose_name='Единовременная закупка')

    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, null=True,
                                       verbose_name='Курируемая группа')

    def __str__(self):
        return f'Рапорт №{self.pk} от {self.creator}'

    class Meta:
        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорта'


class History(models.Model):
    raport = models.ForeignKey(Raport, on_delete=models.PROTECT, verbose_name='Номер рапорта')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    action = models.CharField(max_length=255, verbose_name='Действие')
    action_date = models.DateField(default=now, verbose_name='Дата')


class Files(models.Model):
    file = models.FileField(verbose_name='Файл')
    raport = models.ForeignKey(Raport, on_delete=models.CASCADE, verbose_name='Номер рапорта')
