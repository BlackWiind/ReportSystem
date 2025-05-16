from celery import shared_task
from django.db import transaction
from .models import Report, Files, History
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