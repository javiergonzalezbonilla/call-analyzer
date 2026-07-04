from django.contrib.auth.hashers import make_password
from django.db import migrations

from users.models import User
from django.conf import settings


def seed_users(apps, schema_editor):
    admin = User.objects.filter(role="admin").first()
    password = settings.ADMIN_PASSWORD

    if not admin:
        admin = User(
            email=settings.ADMIN_EMAIL,
            role="admin",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            first_name="",
            last_name="",
            password=make_password("admin1234"),
        )
        admin.save()


class Migration(migrations.Migration):

    dependencies = [("users", "0001_initial")]

    operations = [migrations.RunPython(seed_users)]
