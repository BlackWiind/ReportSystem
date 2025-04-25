import json
import os

import requests
import logging

from config.celery import app
from datetime import date

from users.models import VocationsSchedule


logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=5 * 60)
def chek_vocations(self):
    vocations_start = VocationsSchedule.objects.filter(vocation_start=date.today())
    vocations_end = VocationsSchedule.objects.filter(vocation_end=date.today())

    for vocation in vocations_start:
        vocation.deputy.groups.add(vocation.group)
        vocation.vocation_user.is_active = False

    for vocation in vocations_end:
        vocation.deputy.groups.remove(vocation.group)
        vocation.vocation_user.is_active = True
        vocation.delete()


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def notification_api_connect(self, user_id: int, report_id: int, message: str):
    try:
        payload={'user': user_id, 'model_id': report_id, 'message': message}
        response = requests.post(
            os.getenv('NOTIFICATIONS_API_URL'),
            data=json.dumps(payload),
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Notification sent to user {user_id}. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send notification: {e}")
        self.retry(exc=e)
