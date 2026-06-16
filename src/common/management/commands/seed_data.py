import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from social_entities.models import Platform

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates initial admin user and platforms'

    def handle(self, *args, **options):
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin')

        if not User.objects.filter(username=admin_username).exists():
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
            )
            self.stdout.write(f'Superuser "{admin_username}" created')
        else:
            self.stdout.write(f'Superuser "{admin_username}" already exists')

        platforms = [
            {'alias': 'VK', 'name': 'ВКонтакте'},
            {'alias': 'TG', 'name': 'Telegram'},
        ]

        for p in platforms:
            obj, created = Platform.objects.get_or_create(
                alias=p['alias'],
                defaults={'name': p['name']},
            )
            if created:
                self.stdout.write(f'Platform "{p["name"]}" created')
            else:
                self.stdout.write(f'Platform "{p["name"]}" already exists')
