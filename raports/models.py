import os.path

from django.urls import reverse
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


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    action = models.CharField(max_length=255, verbose_name='Действие')
    action_date = models.DateField(default=now, verbose_name='Дата')

    class Meta:
        ordering = ['-id']


def file_directory_path(instance, filename):
    return 'raport_{0}/{1}'.format(instance.pk, filename)


class Files(models.Model):
    file = models.FileField(upload_to="files/%Y/%m/%d/", verbose_name='Файл')

    def filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'


class Raport(models.Model):
    status_choices = (
        ('created', 'Создан'),
        ('approved_by_curator', 'Одобрен куратором'),
        ('approved_by_director', 'Одобрен главным врачём'),
        ('in_purchasing_department', 'В отделе закупок'),
        ('rejected', 'Отклонён'),
    )

    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создатель рапорта')
    text = models.TextField(verbose_name='Текст')
    justification = models.TextField(verbose_name='Основание')
    union = models.BooleanField(default=False, verbose_name='Объеденённый рапорт')
    status = models.CharField(max_length=255, choices=status_choices, default='created', verbose_name='Статус')
    rejection_reason = models.TextField(null=True)
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    price = models.FloatField(default=0.00, verbose_name='Цена')
    one_time = models.BooleanField(default=True, verbose_name='Единовременная закупка')
    history = models.ManyToManyField(History, verbose_name='История')
    files = models.ManyToManyField(Files, verbose_name='Прикреплённые файлы', null=True)

    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, null=True,
                                       verbose_name='Курируемая группа')

    def __str__(self):
        return f'Рапорт №{self.pk} от {self.creator}'

    def get_absolute_url(self):
        return reverse('raports:details', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорта'

        ordering = ['-id']
