from django.db.models.signals import pre_save
from django.dispatch import receiver

from reports.models import Report


class TrackedChanges:
    def __init__(self):
        self.changes = {}


tracked_changes = TrackedChanges()


@receiver(pre_save, sender=Report)
def track_model_changes(sender, instance, **kwargs):
    if instance.pk:
        print('tracker worked')
        try:
            original = sender.objects.get(pk=instance.pk)
            changes = {}

            # Получаем только те поля, которые были в запросе
            for field in instance._meta.fields:
                field_name = field.name
                original_value = getattr(original, field_name)
                new_value = getattr(instance, field_name)

                # Проверяем, изменилось ли значение
                if original_value != new_value:
                    # Используем verbose_name или обычное имя поля
                    verbose_name = getattr(field, 'verbose_name', field_name)
                    changes[verbose_name] = new_value
            print(changes)

            tracked_changes.changes[instance.pk] = changes

        except sender.DoesNotExist:
            pass