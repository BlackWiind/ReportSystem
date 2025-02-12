import os.path

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now

from django.db import models

from users.models import User, CuratorsGroup, Statuses

class DraftQuerySet(models.QuerySet):
    def not_closed(self):
        return self.filter(closed=False)

    def closed(self):
        return self.filter(closed=True)

class DraftManager(models.Manager):
    def get_queryset(self):
        return DraftQuerySet(self.model)

    def not_closed(self, user):
        if user.custom_permissions.name == 'head_of_department':
            return self.get_queryset().not_closed().filter(creator__department=user.department)
        return self.get_queryset().not_closed().filter(creator=user)

    def closed(self):
        return self.get_queryset().closed()

def report_directory_path(instance, filename):
    return 'print_forms/report_{0}/{1}'.format(instance.id, filename)


def file_directory_path(instance, filename):
    return 'report_{0}/{1}'.format(instance.pk, filename)


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name='Тэг')

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


class Files(models.Model):
    file = models.FileField(upload_to="files/%Y/%m/%d/", verbose_name='Файл')

    def filename(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'


class SourcesOfFunding(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Источник финансирования'
        verbose_name_plural = 'Источники финансирования'

class GeneralData(models.Model):
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор',
                                related_name='%(app_label)s_%(class)s_creator')
    text = models.TextField(verbose_name='Текст')
    justification = models.TextField(verbose_name='Основание')
    price = models.FloatField(default=0.00, verbose_name='Цена')
    one_time = models.BooleanField(default=True, verbose_name='Единовременная закупка')
    tags = models.ManyToManyField(Tag, verbose_name='Теги', related_name='%(app_label)s_%(class)s_tags')
    date_create = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        abstract = True


class Draft(GeneralData):
    closed = models.BooleanField(default=False, verbose_name='Закрыта')
    close_reason = models.TextField(null=True, blank=True, verbose_name='Причина закрытия')

    objects = models.Manager()
    custom_query = DraftManager()

class Report(GeneralData):
    union = models.BooleanField(default=False, verbose_name='Объеденённый рапорт')
    status = models.ForeignKey(Statuses, null=True, on_delete=models.PROTECT, default=1, verbose_name='Статус')
    rejection_reason = models.TextField(null=True, blank=True)
    history = models.ManyToManyField(History, verbose_name='История', blank=True, related_name='history')
    files = models.ManyToManyField(Files, verbose_name='Прикреплённые файлы', blank=True)
    print_form = models.FileField(upload_to=report_directory_path, blank=True)

    curators_group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, null=True,
                                       verbose_name='Курируемая группа')

    assigned_purchasing_specialist = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True,
                                                       verbose_name='Специалист отдела закупок',
                                                       related_name='assigned_purchasing_specialist')
    responsible = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True,
                                    verbose_name='Ответственный специалист',
                                    related_name='responsible')

    sources_of_funding = models.ManyToManyField(SourcesOfFunding, verbose_name='Источники финансирования',
                                                blank=True, related_name='%(app_label)s_%(class)s_sources')
    sign = models.TextField(verbose_name='ЭЦП', blank=True)
    waiting = models.BooleanField(default=False, verbose_name='Ожидание')
    parents = models.ManyToManyField(Draft, blank=True, related_name='%(app_label)s_%(class)s_sources')


    def __str__(self):
        return f'Рапорт №{self.pk} от {self.creator}'

    def get_absolute_url(self):
        return reverse('reports:details', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорта'

        ordering = ['-id']



@receiver(pre_delete, sender=Report)
def delete_related_jobs(sender, instance, **kwargs):
    for history in instance.history_set.all():
        # No remaining projects
        if not history.projects.exclude(id=instance.id).count():
            history.delete()
    for file in instance.files_set.all():
        # No remaining projects
        if not file.projects.exclude(id=instance.id).count():
            file.delete()


class WaitingStatusForUser(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель', related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Получатель')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name='Рапорт')
    date_of_creation = models.DateField(auto_now_add=True, verbose_name='Дата создания')