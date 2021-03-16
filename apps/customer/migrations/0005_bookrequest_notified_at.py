from django.db import migrations
from django.utils import timezone

from apps.customer.models import BookRequest


def set_notified_at(apps, schema_editor):
    now = timezone.now()
    BookRequest.objects.update(notified_at=now, feedback_requested_at=now)


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_bookrequest_notified_at'),
    ]

    operations = [
        migrations.RunPython(set_notified_at)
    ]