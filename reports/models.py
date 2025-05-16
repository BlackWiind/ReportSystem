import os.path

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django.core.validators import MinValueValidator

from django.db import models, transaction
from minio_storage.storage import MinioStorage

from reports.managers import ReportManager
from users.models import User, CuratorsGroup, Statuses

import logging
logger = logging.getLogger(__name__)



def report_directory_path(instance, filename):
    return 'print_forms/report_{0}/{1}'.format(instance.id, filename)


def file_directory_path(instance, filename):
    return 'report_{0}/{1}'.format(instance.pk, filename)


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name='Тэг')
    group = models.ForeignKey(CuratorsGroup, on_delete=models.CASCADE, verbose_name='Группа', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

        ordering = ['name',]


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    action_date = models.DateField(default=now, verbose_name='Дата')
    text = models.TextField(blank=True, verbose_name='Text')

    class Meta:
        ordering = ['-action_date', '-id']


class Files(models.Model):
    file = models.FileField(upload_to="files/%Y/%m/%d/", verbose_name='Файл')

    def filename(self):
        return os.path.basename(self.file.name)

    def file_exists_in_minio(self):
        """Проверяет, существует ли файл в Minio."""
        if not self.file:
            return False
        storage = self.file.storage
        return storage.exists(self.file.name)

    def delete(self, *args, **kwargs):
        """Удаляет файл из Minio и запись из БД."""
        with transaction.atomic():
            if self.file:
                try:
                    if self.file_exists_in_minio():
                        self.file.delete(save=False)
                        logger.info(f"Файл {self.id} удалён из Minio")
                except Exception as e:
                    logger.error(f"Ошибка при удалении файла {self.file.name}: {e}")
                    raise
        super().delete(*args, **kwargs)

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


class Report(models.Model):
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Автор',
                                related_name='%(app_label)s_%(class)s_creator')
    text = models.TextField(verbose_name='Текст')
    justification = models.TextField(verbose_name='Основание', null=True, blank=True)
    price = models.FloatField(default=0.00, verbose_name='Цена')
    one_time = models.BooleanField(default=True, verbose_name='Единовременная закупка')
    tags = models.ManyToManyField(Tag, verbose_name='Теги', related_name='%(app_label)s_%(class)s_tags')
    date_create = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    union = models.BooleanField(default=False, verbose_name='Объединённый рапорт')
    status = models.ForeignKey(Statuses, null=True, on_delete=models.PROTECT, default=1, verbose_name='Статус')
    closed = models.BooleanField(default=False, verbose_name='Закрыта')
    history = models.ManyToManyField(History, verbose_name='История', blank=True,
                                     related_name='%(app_label)s_%(class)s_sources')
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
    draft = models.BooleanField(default=False, verbose_name='Черновик')
    parents = models.ManyToManyField(
        'self', blank=True, verbose_name='Родитель', related_name='%(app_label)s_%(class)s_sources'
    )

    objects = models.Manager()
    custom_query = ReportManager()


    def __str__(self):
        return f'Рапорт №{self.pk} от {self.creator}'

    def get_absolute_url(self):
        return reverse('reports:details', kwargs={'pk': self.pk})

    def next_status(self, user, history_text=None):
        """Перевод рапорта на следующий статус (если возможно)."""
        if not self.status:
            raise ValueError("Статус не установлен...")

        if self.status.is_final:
            raise ValueError("Это *финальный* статус.")

        if not self.status.next_status:
            raise ValueError("Следующего статуса нет...")

        self.status = self.status.next_status
        self.save()
        default_text = f"Статус изменён автоматически на {self.status.name}"
        self._add_history_entry(user, history_text if history_text else default_text)
        return self.status

    def prev_status(self, user, history_text=None):
        """Откат рапорта на предыдущий статус (если возможно)."""
        if not self.status:
            raise ValueError("Нет статуса... Ты издеваешься?")

        previous_statuses = Statuses.objects.filter(next_status=self.status)

        if not previous_statuses.exists():
            raise ValueError("Это *начальный* статус.")

        # Подставить правельные данные вместо some
        if self.status.name == 'some':
            previous_statuses = Statuses.objects.filter(next_status=previous_statuses.first())

        if previous_statuses.count() > 1:
            raise ValueError("Множество предыдущих статусов... Ты напортачил с логикой, иди *фикси*!")

        self.status = previous_statuses.first()
        self.save()
        default_text = f"Статус откачен на {self.status.name}"
        self._add_history_entry(user, history_text if history_text else default_text)
        return self.status

    def set_status_manually(self, user, new_status, history_text=None):
        """Ручная установка статуса."""
        if not isinstance(new_status, Statuses):
            raise TypeError("Это вообще не статус...")

        # Проверяем, что новый статус в принципе существует в цепочке (опционально)
        current = self.status
        found = False
        while current:
            if current == new_status:
                found = True
                break
            current = current.next_status

        if not found:
            raise ValueError("Этот статус *не в цепочке*... Ты что, *нарушаешь логику*?")

        self.status = new_status
        self.save()
        default_text = f"Статус изменён вручную на {self.status.name}"
        self._add_history_entry(user, history_text if history_text else default_text)
        return self.status

    def _add_history_entry(self, user, text):
        history_entry = History.objects.create(
            user=user,
            text=text
        )
        self.history.add(history_entry)

    def delete(self, *args, **kwargs):
        if kwargs.pop('async_mode', False):
            from .tasks import async_delete_report_related
            async_delete_report_related.delay(self.id)
        else:
            self._delete_related_sync()
            super().delete(*args, **kwargs)

    def _delete_related_sync(self):
        """Синхронное удаление связанных объектов"""
        for file in self.files.all():
            file.delete()
        for history in self.history.all():
            history.delete()

    class Meta:
        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорты'

        ordering = ['-id']



@receiver(pre_delete, sender=Report)
def delete_report_related(sender, instance, **kwargs):
    if kwargs.get('async_mode', True):
        instance.delete(async_mode=True)
        raise Exception("Отмена синхронного удаления (задача в Celery)")
    else:
        instance._delete_related_sync()


class WaitingStatusForUser(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель', related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Получатель')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name='Рапорт')
    date_of_creation = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Статус ожидания'
        verbose_name_plural = 'Статусы ожидания'

        ordering = ['-date_of_creation']