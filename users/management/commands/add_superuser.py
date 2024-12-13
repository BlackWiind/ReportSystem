import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

username = os.getenv('ADMIN_USER')
password = os.getenv('ADMIN_PASSWORD')

class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            get_user_model().objects.create_superuser(username=username, password=password, department_id=1, email='')