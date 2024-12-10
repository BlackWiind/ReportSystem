from config.celery import app
from datetime import date

from users.models import VocationsSchedule


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
