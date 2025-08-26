# signals.py
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver

from reports.models import Report


class TrackedChanges:
    def __init__(self):
        self.changes = {}
        self.m2m_changes = {}


tracked_changes = TrackedChanges()


@receiver(pre_save, sender=Report)
def track_model_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            changes = {}

            # Обычные поля
            for field in instance._meta.fields:
                if field.name in ['created_at', 'updated_at', 'id']:
                    continue

                original_value = getattr(original, field.name)
                new_value = getattr(instance, field.name)

                if original_value != new_value:
                    verbose_name = getattr(field, 'verbose_name', field.name)
                    changes[verbose_name] = new_value

            if changes:
                tracked_changes.changes[instance.pk] = changes

        except sender.DoesNotExist:
            pass


@receiver(m2m_changed)
def track_m2m_changes(sender, instance, action, reverse, model, pk_set, **kwargs):
    # Обрабатываем только M2M поля модели Report
    if action in ["post_add", "post_remove", "post_clear"] and isinstance(instance, Report):
        if action == "post_clear":
            # Для clear action pk_set is None
            changes = {f"{sender._meta.verbose_name}": "Все элементы удалены"}
        else:
            # Получаем имена объектов
            objects = model.objects.filter(pk__in=pk_set)
            object_names = [str(obj) for obj in objects]

            field_name = None
            # Находим поле M2M по related model
            for field in instance._meta.many_to_many:
                if field.remote_field.model == model:
                    field_name = getattr(field, 'verbose_name', field.name)
                    break

            if field_name:
                if action == "post_add":
                    changes = {field_name: f"Добавлены: {', '.join(object_names)}"}
                else:  # post_remove
                    changes = {field_name: f"Удалены: {', '.join(object_names)}"}
            else:
                changes = {f"M2M поле": f"Изменения в {model._meta.verbose_name}"}

        # Сохраняем M2M изменения
        tracked_changes.m2m_changes[instance.pk] = changes