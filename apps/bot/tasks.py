from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.utils import timezone
from telebot import TeleBot
from telebot.apihelper import ApiException

from apps.bot.models import WorkingHours, SeatsManager, Message
from apps.bot.sync_keyboards import feedback_choice, book_notification
from apps.customer.models import BookRequest

bot = TeleBot(settings.TELEGRAM_TOKEN)


@periodic_task(run_every=crontab(minute='*'), name='renew_additional_seats', ignore_result=True)
def renew_additional_seats():
    now = timezone.now().astimezone().replace(tzinfo=None)
    working_hours = WorkingHours.objects.first()

    today_end_datetime = (timezone.datetime.combine(now.date(), working_hours.end_time))

    if today_end_datetime.time() <= working_hours.start_time:
        today_end_datetime += timezone.timedelta(days=1)

    if today_end_datetime < now:
        return SeatsManager.objects.update(additional_seats_number=0)


@periodic_task(run_every=crontab(hour=7, minute=0), name='send_feedback', ignore_result=True)
def send_feedback():
    today = timezone.now().date()
    book_requests = BookRequest.objects.filter(
        datetime__date=today - timezone.timedelta(days=1),
        confirmed_at__isnull=False,
        feedback_requested_at__isnull=True
    )

    for request in book_requests:
        try:
            user = request.customer
            locale = user.language

            text = getattr(Message.objects.get(title='feedback_choice'), f'text_{locale}')
            bot.send_message(user.id, text, reply_markup=feedback_choice(locale, request.id))

            request.feedback_requested_at = timezone.now()
            request.save()

        except ApiException:
            pass


@periodic_task(run_every=crontab(minute='*/5'), name='send_book_request_notifications', ignore_result=True)
def send_book_request_notifications():
    now = timezone.now().astimezone().replace(tzinfo=None)
    for request in BookRequest.objects.filter(
            datetime__lte=now,
            datetime__gte=now - timezone.timedelta(minutes=5),
            confirmed_at__isnull=False,
            notified_at__isnull=True
    ):
        try:
            customer = request.customer
            locale = customer.language
            text = getattr(Message.objects.get(title='book_notification'), f'text_{locale}')

            bot.send_message(customer.id, text, reply_markup=book_notification(request.id, locale))

            request.notified_at = timezone.now()
            request.save()

        except ApiException:
            continue
