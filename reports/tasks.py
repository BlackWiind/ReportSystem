from celery import shared_task
from django.db import transaction

from users.models import User
from .models import Report, Files, History
from users.tasks import notification_api_connect
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def async_delete_report_related(self, report_id):
    try:
        with transaction.atomic():
            # Получаем отчет (если он еще существует)
            report = Report.objects.filter(pk=report_id).first()
            if not report:
                logger.warning(f"Report {report_id} уже удален")
                return

            # Удаляем связанные файлы
            for file in report.files.all():
                if file.file:
                    try:
                        file.file.delete(save=False)
                        logger.info(f"Файл {file.id} удален из Minio")
                    except Exception as e:
                        logger.error(f"Ошибка удаления файла {file.id}: {e}")
                file.delete()

            # Удаляем связанную историю
            for history in report.history.all():
                history.delete()

            logger.info(f"Все связанные объекты для Report {report_id} удалены")

    except Exception as e:
        logger.error(f"Ошибка при асинхронном удалении для Report {report_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def async_create_new_notification(model_id: int):
    report = Report.objects.get(pk=model_id)
    current_status = report.status
    list_of_users = [report.creator, report.responsible]

    match current_status.name:
        case 'report_created':
            list_of_users.extend(User.objects.filter(
                custom_permissions__name='curator',
                curators_group=report.curators_group
            ))
        case 'purchasing_department_1' | 'purchasing_department_2':
            if report.assigned_purchasing_specialist:
                list_of_users.append(report.assigned_purchasing_specialist)
        case _:
            list_of_users.extend(User.objects.filter(
                custom_permissions__user_can_view=current_status
            ).distinct())

    message_text = (f'Изменение в рапорте №{report.pk}.\n'
                    f'Текущий статус {report.status.visible_name}') if not report.closed else 'Рапорт закрыт.'

    for user in set(list_of_users):
        if user:
            notification_api_connect.delay(user.pk, report.pk, message_text)
