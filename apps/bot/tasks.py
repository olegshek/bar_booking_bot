from celery.schedules import crontab
from celery.task import periodic_task
from django.utils import timezone

from apps.bot.models import WorkingHours, SeatsManager


@periodic_task(run_every=crontab(minute='*'), name='renew_additional_seats', ignore_result=True)
def renew_additional_seats():
    # if WorkingHours.objects.first().end_time < timezone.now().astimezone().time():
    SeatsManager.objects.update(additional_seats_number=0)
