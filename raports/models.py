import os.path

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now

from django.db import models

from users.models import User, CuratorsGroup, Statuses


def raport_directory_path(instance, filename):
    return 'print_forms/raport_{0}/{1}'.format(instance.id, filename)


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
    action = models.ForeignKey(Statuses, null=True, on_delete=models.PROTECT, verbose_name='Статус')
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

    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Создатель рапорта')
    text = models.TextField(verbose_name='Текст')
    justification = models.TextField(verbose_name='Основание')
    union = models.BooleanField(default=False, verbose_name='Объеденённый рапорт')
    status = models.ForeignKey(Statuses, null=True, on_delete=models.PROTECT, default=1, verbose_name='Статус')
    rejection_reason = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    price = models.FloatField(default=0.00, verbose_name='Цена')
    one_time = models.BooleanField(default=True, verbose_name='Единовременная закупка')
    history = models.ManyToManyField(History, verbose_name='История', blank=True)
    files = models.ManyToManyField(Files, verbose_name='Прикреплённые файлы', blank=True)
    date_create = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    print_form = models.FileField(upload_to=raport_directory_path, blank=True)

    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, null=True,
                                       verbose_name='Курируемая группа')

    assigned_purchasing_specialist = models.ForeignKey(User, on_delete=models.PROTECT, blank=True,null=True,
                                                       verbose_name='Специалист отдела закупок',
                                                       related_name='assigned_purchasing_specialist')

    def __str__(self):
        return f'Рапорт №{self.pk} от {self.creator}'

    def get_absolute_url(self):
        return reverse('raports:details', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорта'

        ordering = ['-id']


@receiver(pre_delete, sender=Raport)
def delete_related_jobs(sender, instance, **kwargs):
    for history in instance.history_set.all():
        # No remaining projects
        if not history.projects.exclude(id=instance.id).count():
            history.delete()
    for file in instance.files_set.all():
        # No remaining projects
        if not file.projects.exclude(id=instance.id).count():
            file.delete()
